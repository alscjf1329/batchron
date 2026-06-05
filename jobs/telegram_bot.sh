#!/bin/bash
# 텔레그램 봇 명령어 핸들러 — 상시 실행
# PM2 또는 직접 실행: bash jobs/telegram_bot.sh

set -euo pipefail

TRADER_PATH="${TRADER_PATH:-/app/auto-trader}"

cd "$TRADER_PATH"
source .venv/bin/activate

python telegram_cmd.py
