from detector.rules.baserule import BaseRule
from detector.event import Event
from typing import Optional

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

class MimeSpoofingRule(BaseRule):
    name = "mime_spoofing"

    def match(self, event: Event, engine) -> Optional[dict]:
        if event.resource != "/upload" or event.action != "SUCCESS":
            return None

        extension = event.metadata.get("extension", "").lower()
        mime_category = event.metadata.get("mime_category", "").lower()

        if mime_category == "image" and extension not in IMAGE_EXTENSIONS:
            reason = "Image MIME with non-image extension"

        elif extension in IMAGE_EXTENSIONS and mime_category != "image":
            reason = "Image extension with non-image MIME"

        else:
            return None

        return {
            "rule": self.name,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "ip": event.ip,
            "extension": extension,
            "mime_category": mime_category,
            "reason": reason,
        }