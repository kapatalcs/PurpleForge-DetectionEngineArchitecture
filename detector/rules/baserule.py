from abc import ABC, abstractmethod
from typing import Optional

from detector.event import Event


class BaseRule(ABC):

    name: str = "base_rule"

    @abstractmethod
    def match(self, event: Event, engine) -> Optional[dict]:
        """
        Event geldiğinde engine tarafından çağrılır.

        :param event: Yeni gelen Event
        :param engine: Global engine (state erişimi için)
        :return:
            - Alert dict (eşleşme varsa)
            - None (eşleşme yoksa)
        """
        pass
