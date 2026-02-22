from datetime import datetime
from detector.event import Event
import json
from core.logger import internal_logger

def parse_ssti_access_control_log(line: str) -> Event:
    try:  
        data = json.loads(line)
        return Event(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            ip=data["ip"],
            action=data["action"],
            user=data.get("user"),
            source=data["lab"],
            metadata=data.get("metadata", {})
        )
    
    except Exception as e:
        internal_logger.warning(f"Parser error: {e}")
        return None
    