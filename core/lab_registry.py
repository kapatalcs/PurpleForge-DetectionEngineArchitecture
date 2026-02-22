from threading import Lock

_active_labs = set()
_lock = Lock()

def add_lab(lab_name: str):
    with _lock:
        _active_labs.add(lab_name)

def remove_lab(lab_name: str):
    with _lock:
        _active_labs.discard(lab_name)

def get_active_labs():
    with _lock:
        return list(_active_labs)