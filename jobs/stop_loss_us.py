"""
stop_loss_us.py - 미국장 손절 감시 잡

Claude 없이 가격만 보고 즉시 손절.
cron (2개):
  */3 23 * * 1-5    평일 23시대 3분마다
  */3 0-4 * * 2-6   화~토 새벽 0~4시 3분마다

손절 기준: -7% (미국장은 변동성이 더 크므로 한국장보다 넉넉하게)
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



def _in_market_hours_us() -> bool:
    now = datetime.now()
    wd  = now.weekday()
    t   = now.hour * 60 + now.minute
    if now.hour >= 23:
        return wd <= 4
    else:
        return t <= 4 * 60 + 30 and wd >= 1


def run():
    if not _in_market_hours_us():
        return

    from dotenv import load_dotenv
    load_dotenv(Path(_TRADER_PATH) / ".env")

    import kis_api
    import settings
    from journal import logger as trade_logger

    stop_pct = settings.STOP_LOSS_PCT_US

    try:
        holdings = kis_api.get_balance_us()
    except Exception as e:
        logger.error(f"미국 잔고 조회 실패: {e}")
        return

    for holding in holdings:
        ticker     = holding.get("pdno", "")
        name       = settings.UNIVERSE_US_MAP.get(ticker, ticker)
        qty        = int(holding.get("hldg_qty", 0))
        profit_pct = float(holding.get("evlu_pfls_rt", 0))
        avg_price  = float(holding.get("pchs_avg_pric", 0))
        exchange   = settings.UNIVERSE_US_EXCH.get(ticker, "NAS")

        if qty <= 0:
            continue

        if profit_pct <= stop_pct:
            logger.warning(
                f"[손절-US] {name}({ticker}) | 손익 {profit_pct:+.2f}% ≤ {stop_pct}% → 즉시 매도"
            )
            try:
                data = kis_api.get_stock_data_us(ticker, exchange)
                kis_api.sell_us(ticker, exchange, qty)
                trade_logger.log_trade(
                    "SELL", code=ticker, name=name,
                    price=data["current"], qty=qty,
                    mode="stop_loss_us",
                    reason=f"손절 {profit_pct:+.2f}% (기준 {stop_pct}%)",
                    avg_buy_price=avg_price, profit_pct=profit_pct,
                )
                logger.info(f"[손절 완료-US] {name}({ticker}) {qty}주 매도")
            except Exception as e:
                logger.error(f"[손절 실패-US] {name}({ticker}): {e}")
        else:
            logger.debug(f"{name}({ticker}) {profit_pct:+.2f}% — 유지")
