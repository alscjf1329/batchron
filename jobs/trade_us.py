"""
trade_us.py - 미국장 자동매매 잡

cron 2개로 자정 넘기는 구간 커버:
  */5 23 * * 1-5    평일 23:00~23:55
  */5 0-4 * * 2-6   화~토 00:00~04:30 (전날 평일 미국장 연속)

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


def _in_market_hours_us() -> bool:
    """
    미국장: 23:00 ~ 04:30 KST
    자정을 넘기므로 두 구간으로 나눠 체크.
    - 23:00~23:59: 평일(월~금)
    - 00:00~04:30: 화~토 (전날 평일 장 연속)
    """
    now = datetime.now()
    wd  = now.weekday()   # 0=월 ... 6=일
    t   = now.hour * 60 + now.minute

    if now.hour >= 23:
        return wd <= 4   # 월~금 23시대
    else:
        return t <= 4 * 60 + 30 and wd >= 1   # 화~토 새벽


def run():
    if not _in_market_hours_us():
        logger.debug("미국장 시간 외 — 스킵")
        return

    logger.info("미국장 매매 시작")
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(_TRADER_PATH) / ".env")

        import runner
        runner.run_brain_mode_us()

        logger.info("미국장 매매 완료")
    except Exception as e:
        logger.exception(f"미국장 매매 오류: {e}")
        raise
