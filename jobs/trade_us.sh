#!/bin/bash
# 미국장 AI 매매 — batchron 또는 수동 실행
# 사용: ./jobs/trade_us.sh

set -euo pipefail

TRADER_PATH="${TRADER_PATH:-/app/auto-trader}"

cd "$TRADER_PATH"
source .venv/bin/activate

python -c "
from dotenv import load_dotenv
load_dotenv('$TRADER_PATH/.env')
import runner
runner.run_brain_mode_us()
"
