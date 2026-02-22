from typing import Optional
from detector.event import Event
from detector.rules.baserule import BaseRule


class SQLIAuthBypassRule(BaseRule):

    name = "sqli_auth_bypass"

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.source != "web_login":
            return None

        if event.action != "LOGIN_SUCCESS":
            return None

        if not event.user:
            return None

        if engine.user_exists(event.source,event.user):
            return None  

        return {
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "user": event.user,
            "reason": "LOGIN_SUCCESS for non-existent user",
        }
