#!/usr/bin/env python3
"""
Link/Cross-Reference Integrity Checker — CTyun Skills Farm.

Verifies that all relative links and cross-references in skill docs
resolve correctly. Checks SKILL.md and all references/*.md files.

Usage:
    # Check all skills
    python3 scripts/check_doc_integrity.py

    # Check specific skills
    python3 scripts/check_doc_integrity.py --dirs ctyun-ecs-ops ctyun-iam-ops

    # JSON output
    python3 scripts/check_doc_integrity.py --json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def extract_links_from_md(filepath: Path) -> List[Dict[str, object]]:
    """Extract all markdown links from a file.

    Returns list of {link, text, line_number}.
    """
    links: List[Dict[str, object]] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError):
        return links

    # Match markdown links: [text](url)
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for line_num, line in enumerate(content.splitlines(), 1):
        for match in pattern.finditer(line):
            text = match.group(1)
            url = match.group(2)
            # Only check relative file links, skip absolute URLs
            if url.startswith(("http://", "https://", "mailto:", "#")):
                continue
            links.append({"link": url, "text": text, "line": line_num})

    return links


def resolve_link(link: str, base_dir: Path) -> Tuple[bool, str]:
    """Resolve a relative link against a base directory.

    Returns (resolved, target_path_or_error).
    """
    # Handle anchor-only links
    if link.startswith("#"):
        return (True, "(anchor)")

    # Resolve relative path
    target = (base_dir / link).resolve()

    # Check if target file exists
    if target.exists():
        return (True, str(target))

    # Try without fragment
    fragment = ""
    if "#" in link:
        link_no_frag = link.split("#")[0]
        if link_no_frag:
            target_no_frag = (base_dir / link_no_frag).resolve()
            if target_no_frag.exists():
                return (True, f"{target_no_frag}#{link.split('#')[1]}")
        else:
            # Fragment-only within same file
            return (True, "(anchor)")

    return (False, f"File not found: {target}")


def check_skill_integrity(skill_dir: Path) -> Dict[str, object]:
    """Check link integrity for a single skill directory."""
    skill_name = skill_dir.name
    results: Dict[str, object] = {
        "skill": skill_name,
        "files_checked": [],
        "total_links": 0,
        "broken_links": [],
        "warnings": [],
        "status": "PASS",
    }

    # Files to check
    md_files = [skill_dir / "SKILL.md"] + sorted(
        (skill_dir / "references").glob("*.md")
    )

    for md_file in md_files:
        if not md_file.is_file():
            if md_file.name == "SKILL.md":
                results["warnings"].append("SKILL.md not found")
            continue

        relative_path = str(md_file.relative_to(skill_dir.parent))
        results["files_checked"].append(relative_path)

        links = extract_links_from_md(md_file)
        results["total_links"] += len(links)

        for link_info in links:
            resolved, detail = resolve_link(
                link_info["link"], md_file.parent
            )
            if not resolved:
                results["broken_links"].append(
                    {
                        "file": relative_path,
                        "line": link_info["line"],
                        "link": link_info["link"],
                        "text": link_info["text"],
                        "error": detail,
                    }
                )

    if results["broken_links"]:
        results["status"] = "FAIL"

    return results


def check_gcl_section_exists(skill_dir: Path) -> bool:
    """Verify ## Quality Gate (GCL) section exists in SKILL.md."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return False
    content = skill_md.read_text(encoding="utf-8")
    return bool(re.search(r"## Quality Gate \(GCL\)", content))


def render_report(results: List[Dict[str, object]]) -> str:
    """Render an ASCII report of integrity check results."""
    lines = ["", "  Document Integrity Check Report:", "  " + "\u2500" * 60]

    total_broken = 0
    for r in results:
        broken = len(r["broken_links"])
        total_broken += broken
        check = r["files_checked"]
        status_icon = "\u2705" if r["status"] == "PASS" else "\u274c"
        lines.append(
            f"  {status_icon} {r['skill']:<22} "
            f"({len(check)} files, {r['total_links']} links, "
            f"{broken} broken)"
        )

        if broken > 0:
            for bl in r["broken_links"]:
                lines.append(
                    f"      \u2716 {bl['file']}:{bl['line']} "
                    f"[{bl['text']}]({bl['link']})  \u2192 {bl['error']}"
                )

        for warn in r.get("warnings", []):
            lines.append(f"      \u26a0 {warn}")

    lines.append("  " + "\u2500" * 60)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)
    lines.append(
        f"  Summary: {passed} PASS, {failed} FAIL / {total} total"
        f" ({total_broken} broken links)"
    )
    lines.append("")

    return "\n".join(lines)


def find_all_skill_dirs() -> List[Path]:
    """Find all ctyun-*-ops skill directories."""
    project_root = Path(__file__).parent.parent
    return sorted(project_root.glob("ctyun-*-ops"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Document Integrity Checker — CTyun Skills Farm",
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

    results = [check_skill_integrity(d) for d in skill_dirs]

    if args.output_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(render_report(results))

    failures = [r for r in results if r["status"] == "FAIL"]
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
