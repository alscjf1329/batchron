import argparse
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
load_dotenv()   # .env에서 TRADER_PATH 등 로드

from scheduler import Scheduler


def setup_logging(log_dir: str = "logs"):
    os.makedirs(log_dir, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, "batchron.log"),
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])


def main():
    parser = argparse.ArgumentParser(description="batchron — cron-style Python batch scheduler")
    parser.add_argument("--config", default="config.yaml", help="config file path (default: config.yaml)")
    parser.add_argument("--tick", type=int, default=30, help="poll interval in seconds (default: 30)")
    args = parser.parse_args()

    setup_logging()
    scheduler = Scheduler(config_path=args.config)
    scheduler.run_forever(tick=args.tick)


if __name__ == "__main__":
    main()
