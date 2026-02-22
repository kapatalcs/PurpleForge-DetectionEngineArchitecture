from typing import Optional
from detector.event import Event
from detector.rules.baserule import BaseRule


class MissingFunctionLevelAccessControlRule(BaseRule):

    name = "missing_function_level_access_control"

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.action != "admin_panel_access":
            return None
        
        role = event.metadata.get("role", "")
        if role == "admin":
            return None
        
        return{
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "user": event.user,
            "reason": "A restricted application function was accessed without proper authorization checks.",
            "role": role
        }