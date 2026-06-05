#!/usr/bin/env python3
"""
Token-Efficiency Budget Checker — CTyun Skills Farm.

Estimates token counts for skill files and checks against specified budgets.
Uses a rough heuristic: ~1.3 tokens per ASCII character, ~2 per CJK character.

Cap values from AGENTS.md §Token Efficiency: SKILL.md soft 400/hard 600 lines,
references soft 300/hard 800 lines.

Usage:
    # Check all skills
    python3 scripts/check_skill_size.py

    # Check specific skills
    python3 scripts/check_skill_size.py --dirs ctyun-ecs-ops ctyun-iam-ops

    # Custom budget
    python3 scripts/check_skill_size.py --max-tokens 12000

    # JSON output
    python3 scripts/check_skill_size.py --json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Token estimation factors
ASCII_TOKENS_PER_CHAR = 1.3  # ~0.75 tokens per word average
CJK_TOKENS_PER_CHAR = 2.0  # CJK characters are denser


def estimate_tokens(text: str) -> int:
    """Estimate token count from text content.

    Uses a simple heuristic:
    - ASCII characters: ~1.3 tokens per char
    - CJK characters: ~2 tokens per char
    """
    ascii_count = 0
    cjk_count = 0

    for char in text:
        if '\u4e00' <= char <= '\u9fff' or '\u3000' <= char <= '\u303f':
            cjk_count += 1
        else:
            ascii_count += 1

    return int(ascii_count * ASCII_TOKENS_PER_CHAR + cjk_count * CJK_TOKENS_PER_CHAR)


def estimate_tokens_for_file(filepath: Path) -> Optional[Dict[str, object]]:
    """Estimate tokens for a single file.

    Returns {filename, characters, estimated_tokens, lines} or None.
    """
    if not filepath.is_file():
        return None

    try:
        content = filepath.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError):
        return None

    return {
        "filename": filepath.name,
        "path": str(filepath),
        "characters": len(content),
        "lines": content.count("\n") + 1,
        "estimated_tokens": estimate_tokens(content),
    }


def check_skill_budgets(
    skill_dirs: List[Path],
    max_tokens: int = 8000,
    max_lines_skill_soft: int = 400,
    max_lines_skill_hard: int = 600,
    max_lines_ref_soft: int = 300,
    max_lines_ref_hard: int = 800,
) -> List[Dict[str, object]]:
    """Check token budgets for each skill.

    Returns list of {skill, files, total_tokens, total_lines, over_budget, status}.
    """
    results = []
    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        if not (skill_dir / "SKILL.md").is_file():
            continue

        files = []

        # Check SKILL.md
        skill_file = estimate_tokens_for_file(skill_dir / "SKILL.md")
        if skill_file:
            skill_file["hard_budget"] = max_lines_skill_hard
            skill_file["soft_budget"] = max_lines_skill_soft
            skill_file["over_budget"] = skill_file["lines"] > max_lines_skill_hard
            skill_file["warning"] = skill_file["lines"] > max_lines_skill_soft
            files.append(skill_file)

        # Check references/*.md
        ref_dir = skill_dir / "references"
        if ref_dir.is_dir():
            for ref_file in sorted(ref_dir.glob("*.md")):
                ref_info = estimate_tokens_for_file(ref_file)
                if ref_info:
                    ref_info["hard_budget"] = max_lines_ref_hard
                    ref_info["soft_budget"] = max_lines_ref_soft
                    ref_info["over_budget"] = ref_info["lines"] > max_lines_ref_hard
                    ref_info["warning"] = ref_info["lines"] > max_lines_ref_soft
                    files.append(ref_info)

        total_tokens = sum(f["estimated_tokens"] for f in files)
        total_lines = sum(f["lines"] for f in files)

        over_budget = total_tokens > max_tokens
        warnings = [
            f for f in files if f.get("over_budget") or f.get("warning")
        ]

        if over_budget or warnings:
            status = "WARN" if over_budget else "WARN"
        else:
            status = "PASS"

        results.append(
            {
                "skill": skill_name,
                "files": files,
                "total_tokens": total_tokens,
                "total_lines": total_lines,
                "budget_tokens": max_tokens,
                "over_budget": over_budget,
                "warnings": [
                    {
                        "file": w["filename"],
                        "lines": w["lines"],
                        "budget": (
                            w.get("hard_budget", 800)
                            if w.get("over_budget")
                            else w.get("soft_budget", 300)
                        ),
                        "reason": (
                            "over hard budget"
                            if w.get("over_budget")
                            else "over soft budget"
                        ),
                    }
                    for w in warnings
                ],
                "status": status,
            }
        )

    return results


def render_results(results: List[Dict[str, object]]) -> str:
    """Render an ASCII table of token budget check results."""
    lines = [
        "",
        "  Token Budget Check Report:",
        "  " + "\u2500" * 70,
        f"  {'Skill':<22} {'Files':<5} {'Tokens':<10} {'Lines':<8} {'Status'}",
        "  " + "\u2500" * 70,
    ]

    for r in results:
        icon = "\u2705" if r["status"] == "PASS" else "\u26a0"
        lines.append(
            f"  {icon} {r['skill']:<22} {len(r['files']):<5} "
            f"{r['total_tokens']:<10} {r['total_lines']:<8} {r['status']}"
        )

        for warn in r.get("warnings", []):
            lines.append(
                f"      \u26a0 {warn['file']}: {warn['lines']} lines "
                f"(budget: {warn['budget']}) - {warn['reason']}"
            )

    lines.append("  " + "\u2500" * 70)

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    over_budget_count = sum(1 for r in results if r.get("over_budget"))
    lines.append(
        f"  Summary: {passed} PASS, {warned} WARN / {total} total"
        f" ({over_budget_count} over token budget)"
    )
    lines.append("")

    return "\n".join(lines)


def find_all_skill_dirs() -> List[Path]:
    """Find all ctyun-*-ops skill directories."""
    project_root = Path(__file__).parent.parent
    return sorted(project_root.glob("ctyun-*-ops"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Token-Efficiency Budget Checker — CTyun Skills Farm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dirs",
        type=str,
        nargs="+",
        default=None,
        help="Skill directories to check (default: all ctyun-*-ops dirs)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8000,
        help="Maximum estimated tokens per skill (default: 8000)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output JSON instead of formatted report",
    )

    args = parser.parse_args()

    if args.dirs:
        skill_dirs = [
            Path(d) if Path(d).is_absolute() else Path(__file__).parent.parent / d
            for d in args.dirs
        ]
    else:
        skill_dirs = find_all_skill_dirs()

    if not skill_dirs:
        print("No skill directories found.", file=sys.stderr)
        sys.exit(0)

    results = check_skill_budgets(skill_dirs, max_tokens=args.max_tokens)

    if args.output_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(render_results(results))

    # Exit code: warn if any skill is over budget
    over_budget = [r for r in results if r.get("over_budget")]
    if over_budget:
        sys.exit(1)


if __name__ == "__main__":
    main()
