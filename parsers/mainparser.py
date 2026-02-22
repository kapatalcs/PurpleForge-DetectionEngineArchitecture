import importlib
from pathlib import Path
import json
from typing import List
from detector.event import Event

STATE_FILE = Path("state/log_offsets.json")


def _load_state() -> dict:
    if STATE_FILE.exists():
        content = STATE_FILE.read_text().strip()
        if content:
            return json.loads(content)
    return {}


def _save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def main_parser(lab_name: str) -> List[Event]:
    module_name = f"parsers.{lab_name}_parser"
    func_name = f"parse_{lab_name}_log"

    module = importlib.import_module(module_name)
    parser = getattr(module, func_name)

    log_path = Path(f"labs/{lab_name}/logs/access.log").resolve()
    state = _load_state()

    key = str(log_path)
    stat = log_path.stat()

    entry = state.get(key, {})
    last_offset = entry.get("offset", 0)
    last_size = entry.get("size", 0)
    last_mtime = entry.get("mtime", 0)


    if stat.st_size < last_offset or stat.st_mtime < last_mtime:
        last_offset = 0

    events: List[Event] = []

    with open(log_path, "r", encoding="utf-8") as f:
        f.seek(last_offset)

        for line in f:
            event = parser(line.strip())
            if event:
                events.append(event)

        state[key] = {
            "offset": f.tell(),
            "size": stat.st_size,
            "mtime": stat.st_mtime
        }

    _save_state(state)
    return events



