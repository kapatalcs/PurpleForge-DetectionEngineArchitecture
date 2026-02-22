from datetime import datetime, timedelta
from typing import Optional, Dict,List
from collections import defaultdict

from detector.event import Event
from detector.rules.baserule import BaseRule

class CredentialStuffingAttackRule(BaseRule):

    name = "credential_stuffing_attack"

    def __init__(
        self,
        min_unique_users: int = 5,
        window_seconds: int = 10,
        max_attempts_per_user: int = 2, 
        attack_gap_seconds: int = 5,
    ):
        self.min_unique_users = min_unique_users
        self.window = timedelta(seconds=window_seconds)
        self.max_attempts_per_user = max_attempts_per_user
        self.attack_gap = timedelta(seconds=attack_gap_seconds)

        self._sessions: Dict[str, dict] = {}

    def match(self, event: Event, engine) -> Optional[dict]:

        if event.action not in ("LOGIN_FAIL", "LOGIN_SUCCESS"):
            return None
        
        if not event.user:
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

        events: List[Event] = [
            e for e in engine.get_events_by_ip(ip)
            if (
                e.user
                and e.action in ("LOGIN_FAIL", "LOGIN_SUCCESS")
                and now - e.timestamp <= self.window
            )
        ]

        if len(events) < self.min_unique_users:
            return None
        
        user_attempts = defaultdict(int)
        ip_attempts = defaultdict(int)
        success_users = set()
        total_attempt = len(events)

        for e in events:
            user_attempts[e.user] += 1
            ip_attempts[e.ip] += 1
            if e.action == "LOGIN_SUCCESS":
                success_users.add(e.user)

        unique_users = len(user_attempts)
        unique_ips = len(ip_attempts)

        max_attempts = max(user_attempts.values())

        if unique_ips != 1:
            return None
        if unique_users < self.min_unique_users:
            return None
        
        if max_attempts > self.max_attempts_per_user:
            return None
        
        if len(success_users)/total_attempt < 0.01:
            return None
        
        if session["alert_sent"]:
            return None

        session["alert_sent"] = True


        return {
            "rule": self.name,
            "timestamp": now.isoformat(),
            "ip": ip,
            "source": event.source,
            "unique_users": unique_users,
            "users": sorted(user_attempts.keys()),
            "success_users": sorted(success_users),
            "first_seen": session["first_seen"].isoformat(),
            "last_seen": session["last_seen"].isoformat(),
            "window_seconds": int(self.window.total_seconds()),
            "reason": "A single source attempted multiple stolen username-password combinations."
        }
    

