from dataclasses import dataclass,field
from datetime import datetime
from typing import Optional,Dict,Any

@dataclass
class Event:
    timestamp: datetime
    ip: str
    user: Optional[str]
    action: str
    source: str
    resource: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw: Optional[str] = None