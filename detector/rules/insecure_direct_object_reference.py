from typing import Optional
from detector.event import Event
from detector.rules.baserule import BaseRule


class InsecureDirectObjectReferenceRule(BaseRule):

    name = "insecure_direct_object_reference"

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.action != "template_view":
            return None
        
        resource_owner = event.metadata.get("resource_owner", "")
        role = event.metadata.get("role", "")

        if event.user == resource_owner:
            return None
        elif role == "admin":
            return None

        
        
        return{
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "user": event.user,
            "reason": "An internal object was accessed by manipulating predictable identifiers without authorization.",
            "resource_owner": resource_owner
        }