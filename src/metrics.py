"""Security metrics tracking for the guarded pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path


class SecurityMetrics:
    """Track guardrail effectiveness over time."""

    def __init__(self):
        self.events = []

    def log_event(self, screen_result: dict, direction: str):
        """Log a screening event."""
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "direction": direction,
            "action": screen_result.get("action"),
            "blocked": screen_result.get("blocked", False),
            "event_id": screen_result.get("event_id"),
        })

    def summary(self) -> dict:
        """Get summary statistics of all events."""
        total = len(self.events)
        blocked = sum(1 for e in self.events if e["blocked"])
        return {
            "total_screenings": total,
            "blocked": blocked,
            "block_rate": blocked / total if total > 0 else 0,
            "by_direction": {
                "input_blocks": sum(
                    1 for e in self.events
                    if e["blocked"] and e["direction"] == "input"
                ),
                "output_blocks": sum(
                    1 for e in self.events
                    if e["blocked"] and e["direction"] == "output"
                ),
            },
        }

    def save(self, path: str = "outputs/security_metrics.json"):
        """Save metrics to JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump({"events": self.events, "summary": self.summary()}, f, indent=2)

    def get_blocked_inputs(self) -> list[dict]:
        """Get all blocked input events for analysis."""
        return [e for e in self.events if e["blocked"] and e["direction"] == "input"]
