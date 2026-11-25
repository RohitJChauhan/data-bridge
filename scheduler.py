import logging
import time

import schedule

from bridge import run
from log_config import setup_logging

setup_logging()
logger = logging.getLogger("scheduler")

INTERVAL_MINUTES = 1   # testing value; change to 60 later


def job():
    logger.info("Running pipeline...")
    try:
        run()
    except Exception:
        logger.exception("Pipeline failed")   # saves the full error details in the log


try:
    job()
    schedule.every(INTERVAL_MINUTES).minutes.do(job)
    logger.info("Scheduler started. Running every %d minute(s).", INTERVAL_MINUTES)
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Scheduler stopped.")