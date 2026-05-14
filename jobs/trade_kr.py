"""
trade_kr.py - 한국장 자동매매 잡

cron: */30 9-15 * * 1-5  (평일 09:00~15:30 매 30분)
batchron이 호출 → auto-trader runner 실행

auto-trader 경로 설정:
  .env의 TRADER_PATH 또는 이 파일 기준 상대경로
"""
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# ── auto-trader 경로 주입 ─────────────────────────────────
_TRADER_PATH = os.environ.get(
    "TRADER_PATH",
    str(Path(__file__).parent.parent.parent / "auto-trader")
)
if _TRADER_PATH not in sys.path:
    sys.path.insert(0, _TRADER_PATH)


def _in_market_hours() -> bool:
    """09:05 ~ 15:20 평일만 실행"""
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = now.hour * 60 + now.minute
    return 9 * 60 + 5 <= t <= 15 * 60 + 20


def run():
    if not _in_market_hours():
        logger.debug("장 시간 외 — 스킵")
        return

    logger.info("한국장 매매 시작")
    try:
        # auto-trader 환경변수 로드 (.env가 auto-trader 디렉토리에 있음)
        from dotenv import load_dotenv
        load_dotenv(Path(_TRADER_PATH) / ".env")

        import runner
        runner.run_brain_mode() if __import__("settings").MODE == "brain" \
            else runner.run_strategy_mode()

        logger.info("한국장 매매 완료")
    except Exception as e:
        logger.exception(f"한국장 매매 오류: {e}")
        raise
