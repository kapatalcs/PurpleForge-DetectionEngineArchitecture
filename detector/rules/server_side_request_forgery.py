from typing import Optional
from detector.event import Event
from detector.rules.baserule import BaseRule


class ServerSideRequestForgeryRule(BaseRule):

    name = "server_side_request_forgery"

    def match(self, event: Event, engine) -> Optional[dict]:
        dangerous_keywords = ["127.0.0.1", "localhost"]

        if event.action != "SUCCESS":
            return None

        user_input = event.metadata.get("user_input", "").lower()

        if not any(keyword in user_input for keyword in dangerous_keywords):
            return None

        return {
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "user": event.user,
            "reason": "Attempt to access localhost via user-controlled URL",
        }
