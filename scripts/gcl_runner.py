#!/usr/bin/env python3
"""
Generator-Critic-Loop (GCL) Orchestrator — CTyun Skills Farm.

Orchestrates the adversarial quality gate loop defined in AGENTS.md §7:

    Generator → Critic → Orchestrator (decide) → PASS / RETRY / ABORT

Supports dry-run mode with mock Generator/Critic for offline testing,
and script plugins for real LLM/CLI execution in production.

Usage:
    # Dry-run (mock generator/critic, no real execution)
    python3 scripts/gcl_runner.py ctyun-ecs-ops --request "create an ecs" --dry-run

    # With external generator and critic scripts (plugin mode)
    python3 scripts/gcl_runner.py ctyun-ecs-ops \\
        --request "delete instance i-abc123" \\
        --skill-dir ./ctyun-ecs-ops \\
        --max-iter 2 \\
        --generator-script /path/to/generator.py \\
        --critic-script /path/to/critic.py

    # Full CLI
    python3 scripts/gcl_runner.py <skill_name> \\
        --request "<user request>" \\
        [--rubric-version v1] \\
        [--max-iter 3] \\
        [--skill-dir ./ctyun-<name>-ops] \\
        [--dry-run] \\
        [--generator-script PATH] \\
        [--critic-script PATH] \\
        [--output PATH]
"""

import argparse
import json
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Protocol


# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_RUBRIC_VERSION = "v1"
DEFAULT_MAX_ITERATIONS = 3
SCORE_VALUES = {0, 0.5, 1}
DESTRUCTIVE_OPS = {"delete", "stop", "resize", "create-image"}
READ_ONLY_OPS = {"list", "describe", "get", "details"}


# ── Data Models ──────────────────────────────────────────────────────────────


@dataclass
class GCLConfig:
    """Configuration for a single GCL run."""

    skill_name: str
    request: str
    rubric_version: str = DEFAULT_RUBRIC_VERSION
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    skill_dir: Optional[Path] = None
    dry_run: bool = False
    generator_script: Optional[Path] = None
    critic_script: Optional[Path] = None
    output_path: Optional[Path] = None
    critic_inject_safety: Optional[float] = None  # for testing ABORT


@dataclass
class GeneratorOutput:
    """Result from a Generator execution."""

    command: str
    args: Dict[str, object]
    exit_code: int
    result_excerpt: str


@dataclass
class CriticScores:
    """Five-dimension rubric scores, each 0 / 0.5 / 1."""

    correctness: float = 1.0
    safety: float = 1.0
    idempotency: float = 1.0
    traceability: float = 1.0
    spec_compliance: float = 1.0


@dataclass
class CriticOutput:
    """Result from a Critic evaluation."""

    scores: CriticScores
    suggestions: List[str] = field(default_factory=list)
    blocking: bool = False


@dataclass
class IterationRecord:
    """One iteration in the GCL loop."""

    iter_num: int
    generator: GeneratorOutput
    critic: CriticOutput
    decision: str  # RETRY | ABORT | RETURN


@dataclass
class GCLTrace:
    """Full trace of a GCL run, persisted as JSON."""

    skill: str
    request: str
    rubric_version: str
    iterations: List[IterationRecord] = field(default_factory=list)
    final: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "skill": self.skill,
            "request": self.request,
            "rubric_version": self.rubric_version,
            "iterations": [
                {
                    "iter": it.iter_num,
                    "generator": asdict(it.generator),
                    "critic": {
                        "scores": asdict(it.critic.scores),
                        "suggestions": it.critic.suggestions,
                        "blocking": it.critic.blocking,
                    },
                    "decision": it.decision,
                }
                for it in self.iterations
            ],
            "final": dict(self.final),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: Path) -> Path:
        """Write the trace to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path


def trace_from_dict(data: dict) -> GCLTrace:
    """Deserialize a GCLTrace from a dict (loaded from JSON)."""
    trace = GCLTrace(
        skill=data["skill"],
        request=data["request"],
        rubric_version=data.get("rubric_version", DEFAULT_RUBRIC_VERSION),
    )
    for it_data in data.get("iterations", []):
        gen = GeneratorOutput(**it_data["generator"])
        critic_scores = CriticScores(**it_data["critic"]["scores"])
        critic = CriticOutput(
            scores=critic_scores,
            suggestions=it_data["critic"].get("suggestions", []),
            blocking=it_data["critic"].get("blocking", False),
        )
        trace.iterations.append(
            IterationRecord(
                iter_num=it_data["iter"],
                generator=gen,
                critic=critic,
                decision=it_data["decision"],
            )
        )
    trace.final = data.get("final", {})
    return trace


# ── Protocols ────────────────────────────────────────────────────────────────


class Generator(Protocol):
    """Protocol for a GCL Generator."""

    def execute(
        self,
        request: str,
        rubric_version: str,
        skill_dir: Optional[Path],
        critic_feedback: Optional[List[str]] = None,
        previous_trace: Optional[dict] = None,
    ) -> GeneratorOutput:
        ...


class Critic(Protocol):
    """Protocol for a GCL Critic."""

    def evaluate(
        self,
        generator_output: GeneratorOutput,
        rubric_version: str,
        skill_dir: Optional[Path],
    ) -> CriticOutput:
        ...


# ── Skill Operation Parsing ──────────────────────────────────────────────────


@dataclass
class SkillOperation:
    """A single operation parsed from a skill's SKILL.md."""

    flow_id: str  # e.g., "A", "B"
    name: str  # e.g., "List ECS Instances"
    cli_command: str  # first bash code block line
    has_safety_gate: bool
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    name_keywords: List[str] = field(default_factory=list)  # from flow name (higher weight)


def parse_flow_id(label: str) -> str:
    """Extract flow ID from 'Flow A:', '1. Create VPC' etc."""
    if m := re.search(r"Flow\s+([A-Z0-9]+):", label):
        return m.group(1)
    if m := re.search(r"^([A-Z0-9]+)[\.:]", label.strip()):
        return m.group(1)
    return label.split()[0][:3]


def extract_cli_command(text_block: str) -> str:
    """Extract first bash or python code block from a text block."""
    for lang in ("bash", "python"):
        m = re.search(rf"```{lang}\s*\n(.+?)\n\s*```", text_block, re.DOTALL)
        if m:
            lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
            if lines:
                if lang == "python":
                    for line in lines:
                        if not line.startswith(("from ", "import ", "#", "//")):
                            return line[:120]
                return lines[0]
    m = re.search(r"```\s*\n(.+?)\n\s*```", text_block, re.DOTALL)
    if m:
        lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
        return lines[0] if lines else ""
    return ""


def build_keywords_from_name(name: str) -> List[str]:
    """Build match keywords from operation name with synonym expansion."""
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    words = set()
    for part in spaced.replace("(", "").replace(")", "").split():
        part_clean = part.strip(",.:;").lower()
        if part_clean and len(part_clean) > 2:
            words.add(part_clean)
            # Add synonyms
            if part_clean in SYNONYMS:
                words.update(s for s in SYNONYMS[part_clean] if len(s) > 2)
    stop_words = {"ecs", "instance", "management"}
    return [w for w in words if w not in stop_words]


def load_skill_operations(skill_dir: Optional[Path]) -> List[SkillOperation]:
    """Parse Execution Flows from SKILL.md."""
    if not skill_dir or not (skill_md := skill_dir / "SKILL.md").is_file():
        return []

    content = skill_md.read_text(encoding="utf-8")
    operations: List[SkillOperation] = []

    flow_pattern = re.compile(
        r"^###\s+(?:(?:Flow\s+([A-Z0-9]+):\s*(.+?))\s*$"
        r"|(\d+)[\.:]\s*(.+?)\s*$"
        r"|(?:Operation:\s*(.+?))\s*$)"
        r"(.+?)(?=^###\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    STOP_WORDS = {"the", "and", "for", "with", "has", "not", "all",
                  "ctyun", "cli", "sdk", "json", "client"}
    BODY_SKIP = ("```", "**", "*", "//", "#", "ctyun", "--", "{{", "from ", "import ")

    for match in flow_pattern.finditer(content):
        body = match.group(6)
        if flow_id_str := match.group(1):
            flow_id, name = flow_id_str, match.group(2).strip()
        elif num := match.group(3):
            flow_id, name = num, match.group(4).strip()
        elif op_name := match.group(5):
            flow_id, name = "?", op_name.strip()
        else:
            continue
        cli_cmd = extract_cli_command(body)
        # Skip non-operation headers (always, even if they have code blocks)
        NON_OP_NAMES = {"SHOULD", "SHOULD NOT", "DO NOT", "CLI", "Variable",
                        "Failure", "Safety", "Changelog", "Overview", "Pre-flight",
                        "Parameters", "Artifacts", "Trigger", "Delegation", "Scope",
                        "Setup", "Credentials", "Development", "Execution",
                        "applicability", "environment", "Token"}
        if any(name.upper().startswith(n) for n in NON_OP_NAMES):
            continue
        # Use inferred command if no code block found (analytical operations)
        if not cli_cmd:
            cli_cmd = _infer_command(name)
        has_safety = "**Safety Gate**" in body or "*Safety Gate*" in body
        name_keywords = build_keywords_from_name(name)
        keywords = list(name_keywords)

        for line in (l.strip() for l in body.splitlines() if l.strip()):
            if line.startswith(BODY_SKIP):
                continue
            keywords.extend(
                w.strip(".,;:!?()\"'").lower()
                for w in line.split()[:5]
                if (w_clean := w.strip(".,;:!?()\"'")).isalpha()
                and len(w_clean) > 2
                and w_clean.lower() not in STOP_WORDS | set(keywords)
            )
            break  # only first descriptive line

        operations.append(SkillOperation(
            flow_id=flow_id, name=name, cli_command=cli_cmd,
            has_safety_gate=has_safety, description=name,
            keywords=keywords, name_keywords=name_keywords,
        ))

    return operations


SYNONYMS = {
    "list": {"show", "get", "view", "describe", "query"},
    "show": {"list", "get", "view", "describe", "query"},
    "delete": {"drop", "remove", "destroy"},
    "create": {"add", "new", "make"},
    "drop": {"delete", "remove", "destroy"},
}


def match_operation(
    request: str, operations: List[SkillOperation]
) -> Optional[SkillOperation]:
    """Match a user request to the best operation using weighted keyword scoring.

    Name-based keywords score 2x, body-based 1x. Synonyms are also matched.
    """
    req_lower = request.lower()
    best_op = None
    best_score = 0

    for op in operations:
        score = 0
        for kw in op.name_keywords:
            if kw in req_lower:
                score += 2
            elif kw in SYNONYMS and any(s in req_lower for s in SYNONYMS[kw]):
                score += 1  # synonym match: 1 point
        for kw in op.keywords:
            if kw in req_lower and kw not in op.name_keywords:
                score += 1
        if score > best_score:
            best_score = score
            best_op = op

    return best_op if best_score > 0 else None


class MockGenerator:
    """Mock Generator — reads SKILL.md to find matching operations."""

    def __init__(self):
        self._ops_cache: Dict[str, List[SkillOperation]] = {}

    def _get_operations(self, skill_dir: Optional[Path]) -> List[SkillOperation]:
        key = str(skill_dir or "")
        if key not in self._ops_cache:
            self._ops_cache[key] = load_skill_operations(skill_dir)
        return self._ops_cache[key]

    def execute(
        self,
        request: str,
        rubric_version: str = DEFAULT_RUBRIC_VERSION,
        skill_dir: Optional[Path] = None,
        critic_feedback: Optional[List[str]] = None,
        previous_trace: Optional[dict] = None,
    ) -> GeneratorOutput:
        """Match request against SKILL.md operations and return result."""
        if ops := self._get_operations(skill_dir):
            if matched := match_operation(request, ops):
                cmd = matched.cli_command or f"ctyun ... {matched.name.lower().replace(' ', '-')}"
                return GeneratorOutput(
                    command=cmd, args={"flow": matched.flow_id, "operation": matched.name},
                    exit_code=0,
                    result_excerpt=f"[mock SKILL.md] Flow {matched.flow_id}: {matched.name} → `{cmd}`",
                )
            names = [f"{op.flow_id}:{op.name}" for op in ops[:5]]
            return GeneratorOutput(
                command="no-match", args={"available": names},
                exit_code=1,
                result_excerpt=f"Unmatched request. Available: {', '.join(names)}",
            )

        cmd = _infer_command(request)
        return GeneratorOutput(
            command=cmd, args={"request": request[:120]},
            exit_code=0,
            result_excerpt=f"[mock fallback] Executed: {cmd}",
        )


DESTRUCTIVE_OPS = {"delete", "stop", "resize", "create-image"}
READ_ONLY_OPS = {"list", "describe", "get", "details"}


class MockCritic:
    """Mock Critic — scores generator output against rubric.md thresholds."""

    def __init__(self, inject_scores: Optional[Dict[str, float]] = None):
        self.inject_scores = inject_scores or {}
        self._rubric_cache: Dict[str, Dict[str, object]] = {}

    def _get_rubric(self, skill_dir: Optional[Path]) -> Dict[str, object]:
        key = str(skill_dir or "")
        if key not in self._rubric_cache:
            self._rubric_cache[key] = load_rubric_from_skill_dir(skill_dir)
        return self._rubric_cache[key]

    def evaluate(
        self,
        generator_output: GeneratorOutput,
        rubric_version: str = DEFAULT_RUBRIC_VERSION,
        skill_dir: Optional[Path] = None,
    ) -> CriticOutput:
        """Score generator output against the skill's rubric."""
        if self.inject_scores:
            scores = CriticScores(**{
                k: v for k, v in self.inject_scores.items()
                if hasattr(CriticScores, k) and v in SCORE_VALUES
            })
            return CriticOutput(scores=scores, blocking=scores.safety == 0)

        cmd = generator_output.command.lower()
        cmd_ok = generator_output.exit_code == 0 and cmd != "no-match"
        suggestions = []

        # Correctness
        correctness = 0.0 if cmd == "no-match" else (1.0 if cmd_ok else 0.0)
        if cmd == "no-match":
            suggestions.append("No matching operation found for request")

        # Safety: destructive ops need user confirmation
        safety = 1.0
        if any(kw in cmd for kw in DESTRUCTIVE_OPS):
            safety = 0.5
            suggestions.append("Destructive operation: require explicit user confirmation")

        # Idempotency
        is_readonly = any(kw in cmd for kw in READ_ONLY_OPS)
        idempotency = 1.0 if is_readonly else 0.5
        if "create" in cmd:
            suggestions.append("Create operation: check for duplicate resource guard")

        # Traceability & Spec Compliance
        traceability = 1.0 if generator_output.command else 0.5
        spec_compliance = 0.5 if cmd == "no-match" else 1.0

        scores = CriticScores(
            correctness=correctness, safety=safety,
            idempotency=idempotency, traceability=traceability,
            spec_compliance=spec_compliance,
        )
        return CriticOutput(scores=scores, suggestions=suggestions,
                            blocking=safety == 0 or correctness == 0)


# ── Script Plugin Implementations ────────────────────────────────────────────


class ScriptPluginGenerator:
    """Generator that delegates to an external script via subprocess.

    I/O contract (stdin → stdout JSON):
        Input:  {"request", "rubric_version", "critic_feedback", "previous_trace"}
        Output: {"command", "args", "exit_code", "result_excerpt"}
    """

    def __init__(self, script_path: Path):
        self.script_path = script_path.resolve()

    def execute(
        self,
        request: str,
        rubric_version: str = DEFAULT_RUBRIC_VERSION,
        skill_dir: Optional[Path] = None,
        critic_feedback: Optional[List[str]] = None,
        previous_trace: Optional[dict] = None,
    ) -> GeneratorOutput:
        """Run the external generator script."""
        input_data = {
            "request": request,
            "rubric_version": rubric_version,
            "critic_feedback": critic_feedback,
            "previous_trace": previous_trace,
        }
        try:
            result = subprocess.run(
                [sys.executable, str(self.script_path)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                return GeneratorOutput(
                    command="plugin-error",
                    args={},
                    exit_code=result.returncode,
                    result_excerpt=result.stderr.strip()[:500],
                )
            output = json.loads(result.stdout)
            return GeneratorOutput(
                command=output.get("command", ""),
                args=output.get("args", {}),
                exit_code=output.get("exit_code", 1),
                result_excerpt=output.get("result_excerpt", ""),
            )
        except subprocess.TimeoutExpired:
            return GeneratorOutput(
                command="timeout",
                args={},
                exit_code=-1,
                result_excerpt="Generator script timed out after 120s",
            )
        except (json.JSONDecodeError, Exception) as e:
            return GeneratorOutput(
                command="plugin-error",
                args={},
                exit_code=1,
                result_excerpt=f"Plugin error: {e}",
            )


class ScriptPluginCritic:
    """Critic that delegates to an external script via subprocess.

    I/O contract (stdin → stdout JSON):
        Input:  {"generator_output": {...}, "rubric_version": "..."}
        Output: {"scores": {...}, "suggestions": [...], "blocking": bool}
    """

    def __init__(self, script_path: Path):
        self.script_path = script_path.resolve()

    def evaluate(
        self,
        generator_output: GeneratorOutput,
        rubric_version: str = DEFAULT_RUBRIC_VERSION,
        skill_dir: Optional[Path] = None,
    ) -> CriticOutput:
        """Run the external critic script."""
        input_data = {
            "generator_output": asdict(generator_output),
            "rubric_version": rubric_version,
        }
        try:
            result = subprocess.run(
                [sys.executable, str(self.script_path)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                return CriticOutput(
                    scores=CriticScores(correctness=0.0, safety=0.0),
                    suggestions=[f"Critic script error: {result.stderr.strip()[:200]}"],
                    blocking=True,
                )
            output = json.loads(result.stdout)
            scores_data = output.get("scores", {})
            scores = CriticScores(
                correctness=scores_data.get("correctness", 1.0),
                safety=scores_data.get("safety", 1.0),
                idempotency=scores_data.get("idempotency", 1.0),
                traceability=scores_data.get("traceability", 1.0),
                spec_compliance=scores_data.get("spec_compliance", 1.0),
            )
            return CriticOutput(
                scores=scores,
                suggestions=output.get("suggestions", []),
                blocking=output.get("blocking", scores.safety == 0),
            )
        except subprocess.TimeoutExpired:
            return CriticOutput(
                scores=CriticScores(correctness=0.0, safety=0.0),
                suggestions=["Critic script timed out after 60s"],
                blocking=True,
            )
        except (json.JSONDecodeError, Exception) as e:
            return CriticOutput(
                scores=CriticScores(correctness=0.0, safety=0.0),
                suggestions=[f"Plugin error: {e}"],
                blocking=True,
            )


# ── Rubric Loading ───────────────────────────────────────────────────────────


def load_rubric_from_skill_dir(skill_dir: Optional[Path]) -> Dict[str, object]:
    """Read references/rubric.md and extract dimension thresholds.

    Returns a dict with per-dimension threshold info or an empty dict
    if the rubric cannot be read.
    """
    if not skill_dir or not (rubric_path := skill_dir / "references" / "rubric.md").is_file():
        return {}

    content = rubric_path.read_text(encoding="utf-8")
    dimensions = {}

    in_table = False
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        if "Dimension" in stripped and "Scale" in stripped:
            in_table = True  # header row
            continue
        if not in_table:
            continue

        parts = [p.strip() for p in stripped.strip("|").split("|")]
        if len(parts) < 4 or set(parts[1]) == {"-"}:
            continue  # skip separator |---|---|---|

        name = parts[1].strip("*").lower().replace(" ", "_")
        dimensions[name] = {"scale": parts[2], "threshold": parts[3]}

    return dimensions


# ── Orchestrator ─────────────────────────────────────────────────────────────


class GCLOrchestrator:
    """Main GCL orchestrator that manages the Generator-Critic-Loop.

    Runs a preflight check, then iterates:
        1. Generate (execute the operation)
        2. Critique (score against rubric)
        3. Decide (PASS / RETRY / ABORT)
    until termination.
    """

    def __init__(self, config: GCLConfig, generator: Generator, critic: Critic):
        self.config = config
        self.generator = generator
        self.critic = critic
        self.trace = GCLTrace(
            skill=config.skill_name,
            request=config.request,
            rubric_version=config.rubric_version,
        )

    def run(self) -> tuple[GCLTrace, str]:
        """Execute the full GCL loop.

        Returns:
            (GCLTrace, final_output_string)
        """
        self._preflight()
        critic_feedback: Optional[List[str]] = None
        previous_trace_dict: Optional[dict] = None

        for iter_num in range(1, self.config.max_iterations + 1):
            # ── Generate ────────────────────────────────────────────────
            gen_output = self.generator.execute(
                request=self.config.request,
                rubric_version=self.config.rubric_version,
                skill_dir=self.config.skill_dir,
                critic_feedback=critic_feedback,
                previous_trace=previous_trace_dict,
            )

            # ── Critique ────────────────────────────────────────────────
            critic_output = self.critic.evaluate(
                generator_output=gen_output,
                rubric_version=self.config.rubric_version,
                skill_dir=self.config.skill_dir,
            )

            # ── Decide ──────────────────────────────────────────────────
            decision, reason = self._decide(critic_output, iter_num)

            record = IterationRecord(
                iter_num=iter_num,
                generator=gen_output,
                critic=critic_output,
                decision=decision,
            )
            self.trace.iterations.append(record)

            if decision == "RETRY":
                critic_feedback = critic_output.suggestions
                previous_trace_dict = gen_output.__dict__.copy()
                continue

            # Terminal: PASS, MAX_ITER, or ABORT
            if decision == "ABORT":
                status = "ABORT"
            elif decision == "MAX_ITER":
                status = "MAX_ITER"
            else:
                status = "PASS"
            self.trace.final = {
                "status": status,
                "iter": iter_num,
                "output": gen_output.result_excerpt,
                "reason": reason,
            }
            return self.trace, gen_output.result_excerpt

    def _preflight(self) -> None:
        """Validate preconditions before starting the loop."""
        if self.config.skill_dir:
            skill_dir = self.config.skill_dir
            if not skill_dir.is_dir():
                print(
                    f"Warning: skill directory not found: {skill_dir}",
                    file=sys.stderr,
                )
                return

            rubric_path = skill_dir / "references" / "rubric.md"
            if not rubric_path.is_file():
                print(
                    f"Warning: rubric.md not found at {rubric_path}",
                    file=sys.stderr,
                )

            # Log available operations
            ops = load_skill_operations(skill_dir)
            if ops:
                print(f"  Loaded {len(ops)} operations from {skill_dir.name}/SKILL.md:")
                for op in ops:
                    sg = " ⚠️" if op.has_safety_gate else ""
                    cmd = op.cli_command[:60] + "..." if len(op.cli_command) > 60 else op.cli_command
                    print(f"    Flow {op.flow_id}: {op.name}{sg}")
                    print(f"      → {cmd}")
                print()

    def _decide(
        self, critic: CriticOutput, iter_num: int
    ) -> tuple[str, Optional[str]]:
        """Apply termination rules from AGENTS.md §5.

        Returns (decision, reason).
        """
        # Rule 1: Safety = 0 → ABORT immediately
        if critic.scores.safety == 0:
            return ("ABORT", "Safety=0: immediate abort")

        # Rule 2: All scores meet threshold → PASS (RETURN)
        if self._all_scores_pass(critic):
            return ("RETURN", "All dimensions pass threshold")

        # Rule 3: Under max_iterations → RETRY
        if iter_num < self.config.max_iterations:
            return ("RETRY", None)

        # Rule 4: Exhausted iterations → return best effort
        return ("MAX_ITER", "Max iterations reached, returning best effort")

    def _all_scores_pass(self, critic: CriticOutput) -> bool:
        """Check if all rubric dimensions meet their thresholds."""
        scores = critic.scores
        # Default threshold: ≥ 0.5 for all dimensions
        thresholds = {
            "correctness": 0.5,
            "safety": 1.0,
            "idempotency": 0.5,
            "traceability": 0.5,
            "spec_compliance": 0.5,
        }
        return all(
            getattr(scores, dim, 0) >= threshold
            for dim, threshold in thresholds.items()
        )

    def persist_trace(self) -> Path:
        """Save the trace to a JSON file. Returns the file path."""
        if self.config.output_path:
            path = self.config.output_path
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            run_id = uuid.uuid4().hex[:8]
            filename = f"gcl-trace-{timestamp}-{run_id}.json"
            path = Path("audit-results") / filename
        return self.trace.save(path)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _infer_command(request: str) -> str:
    """Infer a fallback CLI command from keywords in the request."""
    req_lower = request.lower()
    cmd_map = [
        (("delete", "remove", "destroy", "terminate"), "ctyun delete"),
        (("create", "launch", "new"), "ctyun create"),
        (("stop", "shutdown"), "ctyun stop"),
        (("list", "show", "get", "describe", "query"), "ctyun list"),
    ]
    for keywords, cmd in cmd_map:
        if any(kw in req_lower for kw in keywords):
            return cmd
    return "ctyun describe"


# ── CLI Entry Point ──────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GCL Orchestrator — Generator-Critic-Loop for CTyun Skills Farm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Dry-run with mock generator/critic\n"
            "  %(prog)s ctyun-ecs-ops --request \"create an ecs\" --dry-run\n\n"
            "  # With external scripts\n"
            "  %(prog)s ctyun-ecs-ops --request \"delete i-abc\" \\\n"
            "    --generator-script ./gen.py --critic-script ./crit.py\n"
        ),
    )
    parser.add_argument("skill_name", help="Skill name, e.g. ctyun-ecs-ops")
    parser.add_argument(
        "--request", "-r", required=True, help="User request string (sanitized)"
    )
    parser.add_argument(
        "--rubric-version", default=DEFAULT_RUBRIC_VERSION, help="Rubric version"
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help=f"Max GCL iterations (default: {DEFAULT_MAX_ITERATIONS})",
    )
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=None,
        help="Path to the skill directory (e.g. ./ctyun-ecs-ops)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use mock Generator/Critic (no real execution)",
    )
    parser.add_argument(
        "--generator-script",
        type=Path,
        default=None,
        help="Path to external Generator script (stdin/stdout JSON protocol)",
    )
    parser.add_argument(
        "--critic-script",
        type=Path,
        default=None,
        help="Path to external Critic script (stdin/stdout JSON protocol)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Trace output path (default: audit-results/gcl-trace-<timestamp>.json)",
    )
    parser.add_argument(
        "--critic-inject-safety",
        type=float,
        default=None,
        choices=[0, 0.5, 1],
        help="Inject a safety score (for testing ABORT behavior)",
    )

    args = parser.parse_args()

    # Build config
    skill_dir = args.skill_dir or Path(f"./{args.skill_name}")
    config = GCLConfig(
        skill_name=args.skill_name,
        request=args.request,
        rubric_version=args.rubric_version,
        max_iterations=args.max_iter,
        skill_dir=skill_dir,
        dry_run=args.dry_run,
        generator_script=args.generator_script,
        critic_script=args.critic_script,
        output_path=args.output,
    )

    # Instantiate Generator and Critic
    if args.generator_script:
        generator: Generator = ScriptPluginGenerator(args.generator_script)
    elif args.dry_run:
        generator = MockGenerator()
    else:
        print(
            "Error: No generator specified. Use --dry-run for mock or "
            "--generator-script for plugin mode.",
            file=sys.stderr,
        )
        sys.exit(1)

    inject_scores = {}
    if args.critic_inject_safety is not None:
        inject_scores["safety"] = args.critic_inject_safety

    if args.critic_script:
        critic: Critic = ScriptPluginCritic(args.critic_script)
    elif args.dry_run:
        critic = MockCritic(inject_scores=inject_scores or None)
    else:
        print(
            "Error: No critic specified. Use --dry-run for mock or "
            "--critic-script for plugin mode.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run GCL
    orchestrator = GCLOrchestrator(config=config, generator=generator, critic=critic)
    trace, final_output = orchestrator.run()

    # Output results
    final_status = trace.final.get("status", "UNKNOWN")
    final_reason = trace.final.get("reason", "")

    print(f"\n{'=' * 60}")
    print(f"GCL RESULT: {final_status}")
    print(f"{'=' * 60}")
    print(f"  Skill:      {trace.skill}")
    print(f"  Iterations: {len(trace.iterations)}")
    print(f"  Final iter: {trace.final.get('iter', '?')}")
    if final_reason:
        print(f"  Reason:     {final_reason}")
    print(f"\n  Output: {final_output[:200]}")
    print()

    # Print iteration summary
    for it in trace.iterations:
        s = it.critic.scores
        print(
            f"  Iter {it.iter_num}: [{it.decision}] "
            f"C={s.correctness} S={s.safety} I={s.idempotency} "
            f"T={s.traceability} SC={s.spec_compliance}"
        )
        if it.critic.suggestions:
            for suggestion in it.critic.suggestions:
                print(f"    ↳ {suggestion}")

    # Persist trace
    trace_path = orchestrator.persist_trace()
    print(f"\n  Trace saved: {trace_path.absolute()}")

    # Exit code
    if final_status in ("ABORT", "FAIL"):
        sys.exit(1)


if __name__ == "__main__":
    main()
