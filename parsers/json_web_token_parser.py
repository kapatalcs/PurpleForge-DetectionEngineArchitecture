from datetime import datetime
from detector.event import Event
import json
from core.logger import internal_logger

def parse_json_web_token_log(line: str) -> Event:
    try:
        data = json.loads(line)
        return Event(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            ip=data["ip"],
            user=data.get("user"),
            action=data["action"],
            source=data["lab"],
            resource=data["resource"],
            metadata=data.get("metadata", {}),
            raw=line
        )
        
    
    except Exception as e:
        internal_logger.warning(f"Parser error: {e}")
        return None
    