"""
stop_loss_kr.py - 한국장 손절 감시 잡

Claude 없이 가격만 보고 즉시 손절.
cron: */3 9-15 * * 1-5  (평일 장중 3분마다)

손절 기준: settings.yaml → params.stop_loss (기본 -5%)
"""
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

_TRADER_PATH = os.environ.get(
    "TRADER_PATH",
    str(Path(__file__).parent.parent.parent / "auto-trader")
)
if _TRADER_PATH not in sys.path:
    sys.path.insert(0, _TRADER_PATH)


def _in_market_hours() -> bool:
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = now.hour * 60 + now.minute
    return 9 * 60 + 5 <= t <= 15 * 60 + 20


def run():
    if not _in_market_hours():
        return

    from dotenv import load_dotenv
    load_dotenv(Path(_TRADER_PATH) / ".env")

    import kis_api
    import settings
    from journal import logger as trade_logger

    # 손절 기준: settings.yaml → trading.stop_loss_pct
    stop_pct = settings.STOP_LOSS_PCT

    try:
        holdings = kis_api.get_balance()
    except Exception as e:
        logger.error(f"잔고 조회 실패: {e}")
        return

    for holding in holdings:
        code       = holding.get("pdno", "")
        name       = holding.get("prdt_name", code)
        qty        = int(holding.get("hldg_qty", 0))
        profit_pct = float(holding.get("evlu_pfls_rt", 0))
        avg_price  = float(holding.get("pchs_avg_pric", 0))

        if qty <= 0:
            continue

        if profit_pct <= stop_pct:
            logger.warning(
                f"[손절] {name}({code}) | 손익 {profit_pct:+.2f}% ≤ {stop_pct}% → 즉시 매도"
            )
            try:
                data = kis_api.get_stock_data(code)
                kis_api.sell(code, qty)
                trade_logger.log_trade(
                    "SELL", code=code, name=name,
                    price=data["current"], qty=qty,
                    mode="stop_loss",
                    reason=f"손절 {profit_pct:+.2f}% (기준 {stop_pct}%)",
                    avg_buy_price=avg_price, profit_pct=profit_pct,
                )
                logger.info(f"[손절 완료] {name}({code}) {qty}주 매도")
            except Exception as e:
                logger.error(f"[손절 실패] {name}({code}): {e}")
        else:
            logger.debug(f"{name}({code}) {profit_pct:+.2f}% — 유지")
