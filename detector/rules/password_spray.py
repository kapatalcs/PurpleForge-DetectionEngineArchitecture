from datetime import datetime, timedelta
from typing import Optional, Dict, Set, List

from detector.event import Event
from detector.rules.baserule import BaseRule


class PasswordSprayRule(BaseRule):

    name = "password_spray"

    def __init__(
        self,
        min_unique_users: int = 10,
        window_seconds: int = 20,
        attack_gap_seconds: int = 5,
    ):

        self.min_unique_users = min_unique_users
        self.window = timedelta(seconds=window_seconds)
        self.attack_gap = timedelta(seconds=attack_gap_seconds)

        self._sessions: Dict[str, dict] = {}


    def match(self, event: Event, engine) -> Optional[dict]:
        if event.action != "LOGIN_FAIL":
            return None

        if not event.user or not event.ip:
            return None

        now = event.timestamp
        ip = event.ip

        session = self._sessions.get(ip)

        if not session or now - session["last_seen"] > self.attack_gap:
            session = {
                "first_seen": now,
                "last_seen": now,
                "alert_sent": False,
            }
            self._sessions[ip] = session
        else:
            session["last_seen"] = now

        recent_events: List[Event] = [
            e for e in engine.get_events_by_ip(ip)
            if (
                e.action == "LOGIN_FAIL"
                and e.user
                and now - e.timestamp <= self.window
            )
        ]

        users: Set[str] = {e.user for e in recent_events}

        if len(users) < self.min_unique_users:
            return None

        if session["alert_sent"]:
            return None

        session["alert_sent"] = True

        return {
            "rule": self.name,
            "timestamp": now.isoformat(),
            "source": event.source,
            "ip": ip,
            "unique_users": len(users),
            "users": sorted(users),
            "first_seen": session["first_seen"].isoformat(),
            "last_seen": session["last_seen"].isoformat(),
            "window_seconds": int(self.window.total_seconds()),
            "reason": "A single source attempted one common password across multiple accounts."
        }
