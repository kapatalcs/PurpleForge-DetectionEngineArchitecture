from typing import Optional
from detector.event import Event
from detector.rules.baserule import BaseRule

class JsonWebTokenNoneAlgorithmRule(BaseRule):

    name = "json_web_token_none_algorithm"

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.action != "JWT_RECEIVED":
            return None

        algorithm = event.metadata.get("alg", "")
        role = event.metadata.get("role_in_token", "")

        if algorithm != "none" or role != "admin":
            return None

        return {
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "user": event.user,
            "reason": f"JWT NONE ALGORITHM detected with role={role}",
        }