from typing import Optional
from detector.event import Event
from detector.rules.baserule import BaseRule
import re
import json

class ServerSideTemplateInjectionRule(BaseRule):

    name = "server_side_template_injection"

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.action != "template_render":
            return None
        
        ssti_pattern = re.compile(
            r"""
            \{\{.*?(\(|\||__).*?\}\}   |
            \{%.*?(\(|\||__).*?%\}
            """,
            re.VERBOSE
)

        body = event.metadata.get("body","")
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
            
        if not ssti_pattern.search(body):
            return None
        
        return{
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "user": event.user,
            "reason": "User-controlled input was interpreted as a template expression, potentially leading to remote code execution.",
            "body": body
        }