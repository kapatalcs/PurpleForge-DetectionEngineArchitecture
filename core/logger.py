import logging
import os

LOG_DIR = "core/logs"
os.makedirs(LOG_DIR, exist_ok=True)

internal_logger = logging.getLogger("internal")
internal_logger.setLevel(logging.WARNING)

handler = logging.FileHandler(os.path.join(LOG_DIR, "internal.log"))
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
handler.setFormatter(formatter)

internal_logger.addHandler(handler)
