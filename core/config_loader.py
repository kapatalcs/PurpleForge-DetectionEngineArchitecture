import yaml
from typing import List

from detector.rules import RULE_CLASSES
from detector.rules.baserule import BaseRule


class ConfigLoader:
    
    
    def __init__(self, config_path: str | None = None):
        self.config_path = config_path or "configs/config.yaml"
        self._config = self._load_config()


    def _load_config(self) -> dict:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    

    def get_attack_config(self, attack_name) -> dict:
        return self._config.get("attacks", {}).get(attack_name)
    
    def get_lab_config(self) -> dict:
        return self._config.get("labs", {})


    def get_engine_config(self) -> dict:
        return self._config.get("engine", {})


