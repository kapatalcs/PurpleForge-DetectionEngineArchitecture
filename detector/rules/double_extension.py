from datetime import datetime, timedelta
from typing import Optional, Dict,List
from collections import defaultdict

from detector.event import Event
from detector.rules.baserule import BaseRule

class DoubleExtensionRule(BaseRule):
    name = "double_extension"

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.action == "FAIL":
            return None
        
        if not event.ip:
            return None
        
        extension_count = event.metadata.get("extension_count")
        if not extension_count or extension_count <= 1:
            return None
        
        return {
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "extension_count": extension_count,
            "reason": "uploaded file has more than one extension count",
        }

        
