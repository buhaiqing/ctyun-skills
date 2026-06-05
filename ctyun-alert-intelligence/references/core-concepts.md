# Alert Intelligence — Core Concepts

## Key Terms

- **Alarm Rule**: A condition defined in Cloud Monitor that triggers when a metric crosses a threshold
- **Alarm Event**: A single firing of an alarm rule (includes state transitions: ok → alarm → ok)
- **Noise**: Repeated, non-actionable alarm events (often auto-resolved within minutes)
- **Correlation**: Two or more alarms that frequently fire together (indicates shared root cause)
- **Time-to-Acknowledge (TTA)**: Duration between alarm firing and first user action
- **Time-to-Resolve (TTR)**: Duration between alarm firing and resolution

## Analysis Scope

This skill operates on historical alarm data only — it cannot predict future alerts.
