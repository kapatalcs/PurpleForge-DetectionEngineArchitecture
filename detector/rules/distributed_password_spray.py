from datetime import timedelta
from typing import Optional, Set, List
from detector.event import Event
from detector.rules.baserule import BaseRule


class DistributedPasswordSprayRule(BaseRule):

    name = "distributed_password_spray"

    def __init__(self, min_unique_users=3, min_unique_ips=3, window_seconds=30):
        self.min_unique_users = min_unique_users
        self.min_unique_ips = min_unique_ips
        self.window = timedelta(seconds=window_seconds)
        self._alert_sent = False

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.action != "LOGIN_FAIL":
            return None

        now = event.timestamp

        relevant_events: List[Event] = []

        for ip, queue in engine.events_by_ip.items():
            for e in queue:
                if (
                    e.action == "LOGIN_FAIL"
                    and now - e.timestamp <= self.window
                    and e.user
                    and e.ip
                ):
                    relevant_events.append(e)

        if not relevant_events:
            return None

        unique_users: Set[str] = {e.user for e in relevant_events}
        unique_ips: Set[str] = {e.ip for e in relevant_events}

        if len(unique_users) < self.min_unique_users:
            return None

        if len(unique_ips) < self.min_unique_ips:
            return None

        if self._alert_sent:
            return None

        self._alert_sent = True

        return {
            "rule": self.name,
            "timestamp": now.isoformat(),
            "unique_users": sorted(unique_users),
            "unique_ips": sorted(unique_ips),
            "fail_count": len(relevant_events),
            "window_seconds": int(self.window.total_seconds()),
            "reason": "Multiple IPs attempted one common password across multiple users."
        }