"""예제 잡 — 오래된 로그 정리."""
import logging
import os
import time

logger = logging.getLogger(__name__)

LOG_DIR = "logs"
KEEP_DAYS = 30


def run():
    now = time.time()
    removed = 0
    for fname in os.listdir(LOG_DIR):
        fpath = os.path.join(LOG_DIR, fname)
        if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > KEEP_DAYS * 86400:
            os.remove(fpath)
            removed += 1
    logger.info(f"cleanup_job: removed {removed} old log file(s)")
