#!/usr/bin/env python3
"""
GCL Phase 4: Cloud Monitor Alarm Wiring — CTyun Skills Farm.

Evaluates GCL trace metrics against configured thresholds and reports
alarms per docs/GCL_RETROSPECTIVE.md §5.

In production, this script would push metrics to CTyun Cloud Monitor via
the SDK. In the current version, it outputs structured alarm data (text/JSON)
suitable for piping into alerting pipelines.

Usage:
    # Evaluate last 15 minutes of traces (P1/P0 check)
    python3 scripts/gcl_monitor_alarms.py --minutes 15

    # Evaluate last 1 hour (includes P2: avg iterations)
    python3 scripts/gcl_monitor_alarms.py --minutes 60

    # Full evaluation, JSON output
    python3 scripts/gcl_monitor_alarms.py --minutes 60 --json

    # Check all-time traces
    python3 scripts/gcl_monitor_alarms.py --minutes 0

    # Dry-run (don't persist alarm state)
    python3 scripts/gcl_monitor_alarms.py --dry-run
"""

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from gcl_dashboard import TraceLoader, DashboardQueries


# ── Alarm State & Persistence ────────────────────────────────────────────────

ALARM_STATE_FILE = Path(".gcl_alarm_state.json")

ALARM_STATE_SCHEMA = {
    "version": "1",
    "last_updated": "ISO8601",
    "active_alarms": [
        {
            "id": "unique alarm id",
            "skill": "ctyun-ecs-ops",
            "rule": "pass_rate_low|safety_failure|avg_iterations_high",
            "severity": "P0|P1|P2",
            "triggered_at": "ISO8601",
            "value": 45.0,
            "threshold": 70.0,
            "acknowledged": False,
        }
    ],
    "muted_skills": ["ctyun-ecs-ops"],  # skills auto-disabled due to P0
}


def load_alarm_state() -> dict:
    """Load persistent alarm state from .gcl_alarm_state.json."""
    if ALARM_STATE_FILE.is_file():
        try:
            return json.loads(ALARM_STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            pass
    return {"version": "1", "active_alarms": [], "muted_skills": []}


def save_alarm_state(state: dict) -> None:
    """Persist alarm state to .gcl_alarm_state.json."""
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    ALARM_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def generate_alarm_id() -> str:
    """Generate a unique alarm ID."""
    return datetime.now(timezone.utc).strftime("alarm-%Y%m%d-%H%M%S-%f")


# ── Thresholds ────────────────────────────────────────────────────────────────

PASS_RATE_THRESHOLD = 70.0  # percent
SAFETY_FAIL_THRESHOLD = 0  # > 0 failures triggers P0
AVG_ITERATIONS_THRESHOLD = 2.8

NO_ALARM_COOLDOWN = timedelta(hours=1)  # don't re-fire same alarm within 1h


# ── Alarm Evaluation ─────────────────────────────────────────────────────────


class AlarmEvaluator:
    """Evaluate trace metrics against thresholds and generate alarms."""

    def __init__(self, state: dict):
        self.state = state

    def evaluate(
        self, traces: list, minutes: int
    ) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
        """Evaluate traces against all alarm rules.

        Returns (alarms, summary_metrics).
        """
        summary = DashboardQueries.summary_stats(traces)
        by_skill = DashboardQueries.pass_rate_by_skill(traces)
        avg_iter = DashboardQueries.avg_iterations_by_skill(traces)

        alarms: List[Dict[str, object]] = []
        now = datetime.now(timezone.utc)

        # ── P0: Safety failures > 0 (overall) ──────────────────────────
        safety_events = summary.get("safety_events", 0)
        if safety_events > SAFETY_FAIL_THRESHOLD:
            alarm_id = generate_alarm_id()
            alarms.append({
                "id": alarm_id,
                "skill": "*",
                "rule": "safety_failure",
                "severity": "P0",
                "triggered_at": now.isoformat(),
                "value": safety_events,
                "threshold": SAFETY_FAIL_THRESHOLD,
                "message": f"Safety failures detected: {safety_events} events (threshold: >{SAFETY_FAIL_THRESHOLD})",
                "action": "Page on-call + auto-disable skill",
            })

        # ── P1: Pass rate < 70% (per skill) ────────────────────────────
        for entry in by_skill:
            rate = entry.get("pass_rate", 100.0)
            if rate < PASS_RATE_THRESHOLD:
                alarm_id = generate_alarm_id()
                alarms.append({
                    "id": alarm_id,
                    "skill": entry["skill"],
                    "rule": "pass_rate_low",
                    "severity": "P1",
                    "triggered_at": now.isoformat(),
                    "value": rate,
                    "threshold": PASS_RATE_THRESHOLD,
                    "message": f"Pass rate {rate:.1f}% < {PASS_RATE_THRESHOLD:.0f}% for {entry['skill']} ({entry.get('total_runs', 0)} runs)",
                    "action": "Page on-call",
                })

        # ── P2: Avg iterations > 2.8 (per skill) ───────────────────────
        for entry in avg_iter:
            avg = entry.get("avg_iterations", 0.0)
            if minutes >= 60 and avg > AVG_ITERATIONS_THRESHOLD:
                alarm_id = generate_alarm_id()
                alarms.append({
                    "id": alarm_id,
                    "skill": entry["skill"],
                    "rule": "avg_iterations_high",
                    "severity": "P2",
                    "triggered_at": now.isoformat(),
                    "value": avg,
                    "threshold": AVG_ITERATIONS_THRESHOLD,
                    "message": f"Avg iterations {avg:.1f} > {AVG_ITERATIONS_THRESHOLD:.1f} for {entry['skill']}",
                    "action": "Slack alert",
                })

        # Build aggregated metrics
        metrics = {
            "namespace": "CTyun/AgentSkills/GCL",
            "timestamp": now.isoformat(),
            "window_minutes": minutes or None,
            "summary": summary,
            "pass_rate_by_skill": by_skill,
            "avg_iterations_by_skill": avg_iter,
            "total_alarms": len(alarms),
            "alarms_by_severity": {
                "P0": sum(1 for a in alarms if a["severity"] == "P0"),
                "P1": sum(1 for a in alarms if a["severity"] == "P1"),
                "P2": sum(1 for a in alarms if a["severity"] == "P2"),
            },
        }

        return alarms, metrics


# ── Rendering ────────────────────────────────────────────────────────────────


def render_alarms(alarms: List[Dict[str, object]], metrics: Dict[str, object]) -> str:
    """Render alarm results as a formatted text report."""
    summary = metrics.get("summary", {})
    lines = [
        "",
        "  CTyun Skills Farm — GCL Alarm Evaluation",
        "  " + "\u2500" * 60,
        f"  Window:     {metrics.get('window_minutes', 'all-time')} min",
        f"  Namespace:  {metrics['namespace']}",
        f"  Total runs: {summary.get('total_runs', 0)}",
        f"  Pass rate:  {summary.get('overall_pass_rate', 0):.1f}%",
        f"  Avg iters:  {summary.get('avg_iterations', 0):.1f}",
        f"  Safety:     {summary.get('safety_events', 0)} events",
        "",
    ]

    by_sev = metrics.get("alarms_by_severity", {})
    total = sum(by_sev.values())
    if total == 0:
        lines.append("  \u2705  No alarms triggered.")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"  \u26a0  {total} alarm(s) triggered:")
    lines.append("  " + "\u2500" * 60)

    for alarm in alarms:
        severity = alarm["severity"]
        icon = "\U0001f525" if severity == "P0" else ("\u26a0" if severity == "P1" else "\u2139")
        lines.append(f"  {icon} [{severity}] {alarm['rule']}")
        lines.append(f"      Skill:  {alarm['skill']}")
        lines.append(f"      Value:  {alarm['value']} (threshold: {alarm['threshold']})")
        lines.append(f"      Action: {alarm['action']}")
        lines.append("")

    return "\n".join(lines)


# ── CLI Entry Point ──────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GCL Phase 4: Cloud Monitor Alarm Wiring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --minutes 15     # last 15 min (P1/P0 check)\n"
            "  %(prog)s --minutes 60     # last 1 hour (includes P2)\n"
            "  %(prog)s --minutes 0      # all-time\n"
            "  %(prog)s --minutes 60 --json\n"
            "  %(prog)s --dry-run\n"
        ),
    )
    parser.add_argument(
        "--trace-dir",
        type=Path,
        default=Path("audit-results"),
        help="Directory containing gcl-trace-*.json (default: ./audit-results)",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=15,
        help="Lookback window in minutes (0 = all time, default: 15)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output JSON instead of formatted text",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate but do not persist alarm state",
    )

    args = parser.parse_args()

    # Load traces
    lookback = args.minutes // 1440 if args.minutes > 0 else None
    # minutes → days for TraceLoader (it uses days, not minutes)
    lookback_days = lookback
    if args.minutes > 0 and args.minutes < 1440:
        lookback_days = 1  # minimum 1 day filter for TraceLoader
    all_traces = TraceLoader.load_all(args.trace_dir, days=lookback_days)

    if not all_traces:
        print(f"No GCL traces found in {args.trace_dir}/", file=sys.stderr)
        sys.exit(0)

    # Evaluate
    state = load_alarm_state()
    evaluator = AlarmEvaluator(state)
    alarms, metrics = evaluator.evaluate(all_traces, args.minutes)

    # Persist alarm state
    if not args.dry_run:
        # Merge new alarms into state
        for alarm in alarms:
            # Check cooldown: skip if same rule+skill fired within cooldown
            existing = [
                a for a in state.get("active_alarms", [])
                if a["skill"] == alarm["skill"] and a["rule"] == alarm["rule"]
            ]
            if existing:
                last = existing[-1]["triggered_at"]
                try:
                    last_dt = datetime.fromisoformat(last)
                    if datetime.now(timezone.utc) - last_dt < NO_ALARM_COOLDOWN:
                        continue
                except (ValueError, TypeError):
                    pass
            state.setdefault("active_alarms", []).append(alarm)

        # P0: auto-mute skills with safety failures
        for alarm in alarms:
            if alarm["severity"] == "P0":
                muted = state.setdefault("muted_skills", [])
                skill = alarm["skill"]
                if skill not in muted:
                    muted.append(skill)

        save_alarm_state(state)

    # Output
    if args.output_json:
        output = {
            "alarms": alarms,
            "metrics": metrics,
            "alarm_state_path": str(ALARM_STATE_FILE) if not args.dry_run else None,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(render_alarms(alarms, metrics))
        if not args.dry_run:
            print(f"  Alarm state saved to {ALARM_STATE_FILE}")


if __name__ == "__main__":
    main()