#!/usr/bin/env python3
"""
GCL Artifact Presence Checker — CTyun Skills Farm.

Verifies that skills with gcl_mode=required or recommended have all
mandated GCL artifacts (rubric.md, prompt-templates.md, Quality Gate section).

Usage:
    # Check all skills
    python3 scripts/check_gcl_artifacts.py

    # Check specific skills
    python3 scripts/check_gcl_artifacts.py --dirs ctyun-ecs-ops ctyun-iam-ops

    # JSON output
    python3 scripts/check_gcl_artifacts.py --json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


REQUIRED_DIMENSIONS = {
    "correctness",
    "safety",
    "idempotency",
    "traceability",
    "spec_compliance",
}


def parse_gcl_mode(skill_dir: Path) -> Optional[str]:
    """Parse gcl_mode from SKILL.md's ## Quality Gate table.

    Looks for a table row like:
        | `gcl_mode` | `required` | ...
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None

    content = skill_md.read_text(encoding="utf-8")

    # Find the Quality Gate section's parameter table
    in_qg_section = False
    for line in content.splitlines():
        if line.strip().startswith("## Quality Gate"):
            in_qg_section = True
            continue
        if in_qg_section and line.strip().startswith("## "):
            in_qg_section = False
            continue
        if in_qg_section and "gcl_mode" in line and "|" in line:
            # Extract value from table: | `gcl_mode` | `required` | ...
            parts = [p.strip().strip("`").strip() for p in line.split("|")]
            for i, part in enumerate(parts):
                if part == "gcl_mode" and i + 1 < len(parts):
                    val = parts[i + 1].lower()
                    if val in ("required", "recommended", "optional"):
                        return val
    return "unknown"


def check_artifacts_for_skill(skill_dir: Path) -> Dict[str, object]:
    """Check GCL artifact presence for a single skill directory.

    Returns:
        {skill, gcl_mode, rubric, prompt_templates, qg_section,
         rubric_dimensions, warnings, errors, status}
    """
    skill_name = skill_dir.name
    result: Dict[str, object] = {
        "skill": skill_name,
        "gcl_mode": "unknown",
        "rubric": False,
        "prompt_templates": False,
        "qg_section": False,
        "rubric_dimensions": [],
        "missing_dimensions": [],
        "warnings": [],
        "errors": [],
        "status": "SKIP",
    }

    if not (skill_dir / "SKILL.md").is_file():
        result["warnings"].append("No SKILL.md found")
        return result

    # Parse gcl_mode
    gcl_mode = parse_gcl_mode(skill_dir)
    result["gcl_mode"] = gcl_mode or "unknown"

    # Check rubric.md
    rubric_path = skill_dir / "references" / "rubric.md"
    if rubric_path.is_file():
        result["rubric"] = True
        result["rubric_dimensions"] = _check_rubric_dimensions(rubric_path)
    else:
        result["errors"].append("references/rubric.md not found")

    # Check prompt-templates.md
    pt_path = skill_dir / "references" / "prompt-templates.md"
    if pt_path.is_file():
        result["prompt_templates"] = True
    else:
        result["errors"].append("references/prompt-templates.md not found")

    # Check Quality Gate section
    skill_md_content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if re.search(r"## Quality Gate \(GCL\)", skill_md_content):
        result["qg_section"] = True
    else:
        result["errors"].append("## Quality Gate (GCL) section missing in SKILL.md")

    # Determine status
    missing_dimensions = [
        d for d in REQUIRED_DIMENSIONS if d not in result["rubric_dimensions"]
    ]
    result["missing_dimensions"] = missing_dimensions
    if missing_dimensions:
        result["warnings"].append(
            f"Missing rubric dimensions: {', '.join(missing_dimensions)}"
        )

    if gcl_mode == "required":
        if result["errors"]:
            result["status"] = "FAIL"
        elif result["warnings"]:
            result["status"] = "WARN"
        else:
            result["status"] = "PASS"
    elif gcl_mode == "recommended":
        if result["errors"]:
            result["status"] = "WARN"
        elif result["warnings"]:
            result["status"] = "WARN"
        else:
            result["status"] = "PASS"
    else:  # optional or unknown
        if result["errors"]:
            result["status"] = "INFO"
        else:
            result["status"] = "PASS"

    return result


def _check_rubric_dimensions(rubric_path: Path) -> List[str]:
    """Check which required dimensions are present in rubric.md.

    Normalizes spaces to underscores for matching (e.g., 'spec compliance'
    matches 'spec_compliance').
    """
    content = rubric_path.read_text(encoding="utf-8").lower().replace(" ", "_")
    found = []
    for dim in REQUIRED_DIMENSIONS:
        if dim in content:
            found.append(dim)
    return found


def render_report(results: List[Dict[str, object]]) -> str:
    """Render an ASCII table report."""
    header = (
        f"{'Skill':<22} {'gcl_mode':<12} {'rubric':<8} {'templates':<10} "
        f"{'QG':<5} {'Dimensions':<18} {'Status'}"
    )
    sep = "\u2500" * len(header)
    lines = ["", "  GCL Artifact Check Report:", f"  {sep}", f"  {header}", f"  {sep}"]

    for r in results:
        dims = ", ".join(r["rubric_dimensions"])
        missing = r["missing_dimensions"]
        dim_display = dims if dims else ("MISS: " + ", ".join(missing) if missing else "-")
        lines.append(
            f"  {r['skill']:<22} {r['gcl_mode']:<12} "
            f"{'OK' if r['rubric'] else 'MISS':<8} "
            f"{'OK' if r['prompt_templates'] else 'MISS':<10} "
            f"{'OK' if r['qg_section'] else 'MISS':<5} "
            f"{dim_display:<18} {r['status']}"
        )

    lines.append(f"  {sep}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    lines.append(f"\n  Summary: {passed} PASS, {warned} WARN, {failed} FAIL / {total} total")

    # Details for non-PASS
    for r in results:
        if r["status"] != "PASS":
            for err in r["errors"]:
                lines.append(f"    \u2716 {r['skill']}: {err}")
            for warn in r["warnings"]:
                lines.append(f"    \u26a0 {r['skill']}: {warn}")

    lines.append("")
    return "\n".join(lines)


def find_all_skill_dirs() -> List[Path]:
    """Find all ctyun-*-ops skill directories in the project root."""
    project_root = Path(__file__).parent.parent
    return sorted(project_root.glob("ctyun-*-ops"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GCL Artifact Presence Checker — CTyun Skills Farm",
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

    results = [check_artifacts_for_skill(d) for d in skill_dirs]

    if args.output_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(render_report(results))

    # Exit code: fail if any required skill has FAIL status
    failures = [r for r in results if r["status"] == "FAIL"]
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
