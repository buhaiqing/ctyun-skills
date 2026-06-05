#!/usr/bin/env python3
"""
GCL Quality Dashboard — CTyun Skills Farm.

Consumes audit-results/gcl-trace-*.json files and outputs quality metrics
as defined in docs/GCL_RETROSPECTIVE.md.

Usage:
    # Show dashboard (last 7 days)
    python3 scripts/gcl_dashboard.py

    # Show raw JSON output
    python3 scripts/gcl_dashboard.py --json

    # Show dashboard for a specific skill
    python3 scripts/gcl_dashboard.py --by-skill ctyun-ecs-ops

    # Custom trace directory and time range
    python3 scripts/gcl_dashboard.py --trace-dir ./audit-results --days 30
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from gcl_runner import GCLTrace, trace_from_dict


# ── Trace Loader ─────────────────────────────────────────────────────────────


class TraceLoader:
    """Load and filter GCL trace files from a directory."""

    @staticmethod
    def load_all(directory: Path, days: Optional[int] = None) -> List[GCLTrace]:
        """Load all gcl-trace-*.json files, optionally filtered by recency."""
        if not directory.is_dir():
            print(f"Warning: trace directory not found: {directory}", file=sys.stderr)
            return []

        traces: List[GCLTrace] = []
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=days)
            if days is not None
            else None
        )

        for fpath in sorted(directory.glob("gcl-trace-*.json")):
            if cutoff is not None:
                mtime = datetime.fromtimestamp(
                    fpath.stat().st_mtime, tz=timezone.utc
                )
                if mtime < cutoff:
                    continue
            try:
                trace = TraceLoader.load_file(fpath)
                traces.append(trace)
            except (json.JSONDecodeError, KeyError, Exception) as e:
                print(
                    f"Warning: skipping malformed trace {fpath.name}: {e}",
                    file=sys.stderr,
                )

        return traces

    @staticmethod
    def load_file(path: Path) -> GCLTrace:
        """Deserialize a single trace file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return trace_from_dict(data)


# ── Dashboard Queries ────────────────────────────────────────────────────────


class DashboardQueries:
    """Static query methods matching GCL_RETROSPECTIVE.md §4.3."""

    @staticmethod
    def summary_stats(traces: List[GCLTrace]) -> Dict[str, object]:
        """Overall summary statistics."""
        total = len(traces)
        if total == 0:
            return {
                "total_runs": 0,
                "overall_pass_rate": 0.0,
                "avg_iterations": 0.0,
                "safety_events": 0,
            }

        passes = sum(1 for t in traces if t.final.get("status") == "PASS")
        total_iters = sum(len(t.iterations) for t in traces)
        safety_events = sum(
            1
            for t in traces
            for it in t.iterations
            if it.critic.scores.safety == 0
        )

        return {
            "total_runs": total,
            "overall_pass_rate": round(passes / total * 100, 1),
            "avg_iterations": round(total_iters / total, 1),
            "safety_events": safety_events,
        }

    @staticmethod
    def pass_rate_by_skill(
        traces: List[GCLTrace],
    ) -> List[Dict[str, object]]:
        """Pass rate grouped by skill."""
        grouped: Dict[str, list] = {}
        for t in traces:
            grouped.setdefault(t.skill, []).append(t)

        results = []
        for skill, items in sorted(grouped.items()):
            total = len(items)
            passes = sum(1 for i in items if i.final.get("status") == "PASS")
            results.append(
                {
                    "skill": skill,
                    "total_runs": total,
                    "pass_count": passes,
                    "pass_rate": round(passes / total * 100, 1) if total > 0 else 0.0,
                }
            )
        return results

    @staticmethod
    def avg_iterations_by_skill(
        traces: List[GCLTrace],
    ) -> List[Dict[str, object]]:
        """Average iterations grouped by skill."""
        grouped: Dict[str, list] = {}
        for t in traces:
            grouped.setdefault(t.skill, []).append(t)

        results = []
        for skill, items in sorted(grouped.items()):
            total_iters = sum(len(i.iterations) for i in items)
            avg = round(total_iters / len(items), 1)
            results.append({"skill": skill, "avg_iterations": avg})
        return results

    @staticmethod
    def safety_failure_heatmap(
        traces: List[GCLTrace],
    ) -> List[Dict[str, object]]:
        """Safety=0 events: [{skill, date, iter, score}, ...]."""
        failures = []
        for t in traces:
            for it in t.iterations:
                if it.critic.scores.safety == 0:
                    failures.append(
                        {
                            "skill": t.skill,
                            "iteration": it.iter_num,
                        }
                    )
        return failures

    @staticmethod
    def iteration_distribution(
        traces: List[GCLTrace],
    ) -> List[Dict[str, object]]:
        """Distribution of total iterations per run."""
        counts: Dict[int, int] = {}
        for t in traces:
            iters = len(t.iterations)
            counts[iters] = counts.get(iters, 0) + 1

        total = len(traces)
        return [
            {
                "iterations": k,
                "count": v,
                "percentage": round(v / total * 100, 1) if total > 0 else 0.0,
            }
            for k, v in sorted(counts.items())
        ]

    @staticmethod
    def all_queries(
        traces: List[GCLTrace],
    ) -> Dict[str, object]:
        """Run all queries and return a combined dict."""
        return {
            "summary": DashboardQueries.summary_stats(traces),
            "pass_rate_by_skill": DashboardQueries.pass_rate_by_skill(traces),
            "avg_iterations_by_skill": DashboardQueries.avg_iterations_by_skill(traces),
            "safety_failures": DashboardQueries.safety_failure_heatmap(traces),
            "iteration_distribution": DashboardQueries.iteration_distribution(traces),
        }


# ── Dashboard Renderer ───────────────────────────────────────────────────────


class DashboardRenderer:
    """ASCII art rendering of dashboard queries."""

    @staticmethod
    def render_summary_header(stats: Dict[str, object]) -> str:
        """Render the summary header box."""
        pass_rate = stats.get("overall_pass_rate", 0)
        avg_iter = stats.get("avg_iterations", 0)
        safety = stats.get("safety_events", 0)
        total = stats.get("total_runs", 0)

        lines = [
            "\u250c" + "\u2500" * 57 + "\u2510",
            "\u2502  CTyun Skills Farm \u2014 GCL Quality Dashboard"
            + " " * 10
            + "\u2502",
            "\u251c" + "\u2500" * 19 + "\u252c" + "\u2500" * 17 + "\u252c" + "\u2500" * 18 + "\u2524",
            f"\u2502  Pass Rate (total={total})  \u2502  Avg Iterations  \u2502  Safety Events  \u2502",
            f"\u2502  {pass_rate:>6.1f}%{' ' * 12}\u2502  {avg_iter:>8.1f}{' ' * 6}\u2502  {safety:>6}{' ' * 10}\u2502",
            "\u2514" + "\u2500" * 19 + "\u2534" + "\u2500" * 17 + "\u2534" + "\u2500" * 18 + "\u2518",
        ]
        return "\n".join(lines)

    @staticmethod
    def render_pass_rate_chart(data: List[Dict[str, object]]) -> str:
        """Render ASCII bar chart of pass rates by skill."""
        if not data:
            return "  (no data)"

        lines = [
            "",
            "  Pass Rate by Skill:",
            "  " + "\u2500" * 50,
        ]

        for entry in data:
            rate = entry.get("pass_rate", 0)
            total = entry.get("total_runs", 0)
            bar_len = int(rate / 100 * 30)
            bar = "\u2588" * bar_len
            lines.append(
                f"  {entry['skill']:<20} {bar:<30} {rate:>5.1f}%  ({total} runs)"
            )

        lines.append("  " + "\u2500" * 50)
        return "\n".join(lines)

    @staticmethod
    def render_iteration_histogram(data: List[Dict[str, object]]) -> str:
        """Render ASCII histogram of iteration distribution."""
        if not data:
            return "  (no data)"

        lines = [
            "",
            "  Iteration Distribution:",
            "  " + "\u2500" * 50,
        ]

        for entry in data:
            iters = entry.get("iterations", 0)
            count = entry.get("count", 0)
            pct = entry.get("percentage", 0)
            bar_len = int(pct / 100 * 30)
            bar = "\u2588" * bar_len
            label = f"{iters} iter{' ' if iters == 1 else 's'}"
            lines.append(f"  {label:<10} {bar:<30} {pct:>5.1f}%  ({count} runs)")

        lines.append("  " + "\u2500" * 50)
        return "\n".join(lines)

    @staticmethod
    def render_safety_heatmap(data: List[Dict[str, object]]) -> str:
        """Render table of safety failures."""
        if not data:
            return "\n  No safety failures. \u2705\n"

        lines = [
            "",
            "  Safety Failures (safety=0 events):",
            "  " + "\u2500" * 50,
            f"  {'Skill':<20} {'Iteration':<10}",
            "  " + "\u2500" * 50,
        ]
        for entry in data:
            lines.append(
                f"  {entry['skill']:<20} {entry['iteration']:<10}"
            )
        lines.append("  " + "\u2500" * 50)
        return "\n".join(lines)

    @staticmethod
    def render_full_dashboard(data: Dict[str, object]) -> str:
        """Render the complete dashboard."""
        parts = [
            DashboardRenderer.render_summary_header(data.get("summary", {})),
        ]

        parts.append(
            DashboardRenderer.render_pass_rate_chart(
                data.get("pass_rate_by_skill", [])
            )
        )

        parts.append(
            DashboardRenderer.render_iteration_histogram(
                data.get("iteration_distribution", [])
            )
        )

        parts.append(
            DashboardRenderer.render_safety_heatmap(
                data.get("safety_failures", [])
            )
        )

        parts.append("")
        return "\n".join(parts)


# ── CLI Entry Point ──────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GCL Quality Dashboard — CTyun Skills Farm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s                          # show dashboard (7d)\n"
            "  %(prog)s --json                   # output raw JSON\n"
            "  %(prog)s --days 30                # last 30 days\n"
            "  %(prog)s --by-skill ctyun-ecs-ops # single skill\n"
        ),
    )
    parser.add_argument(
        "--trace-dir",
        type=Path,
        default=Path("audit-results"),
        help="Directory containing gcl-trace-*.json files (default: ./audit-results)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7, 0 = all time)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output raw JSON instead of formatted dashboard",
    )
    parser.add_argument(
        "--by-skill",
        type=str,
        default=None,
        help="Filter to a specific skill name",
    )

    args = parser.parse_args()

    # Load traces
    lookback = args.days if args.days > 0 else None
    all_traces = TraceLoader.load_all(args.trace_dir, days=lookback)

    if args.by_skill:
        all_traces = [t for t in all_traces if t.skill == args.by_skill]

    if not all_traces:
        print(f"No GCL traces found in {args.trace_dir}/", file=sys.stderr)
        sys.exit(0)

    # Run queries
    queries = DashboardQueries.all_queries(all_traces)

    # Output
    if args.output_json:
        print(json.dumps(queries, indent=2, ensure_ascii=False))
    else:
        print(DashboardRenderer.render_full_dashboard(queries))


if __name__ == "__main__":
    main()
