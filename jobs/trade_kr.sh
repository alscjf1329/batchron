#!/bin/bash
# 한국장 AI 매매 — batchron 또는 수동 실행
# 사용: ./jobs/trade_kr.sh [--force]
# --force: 장 시간 외에도 강제 실행 (수동 테스트용)

set -euo pipefail

TRADER_PATH="${TRADER_PATH:-/app/auto-trader}"
FORCE=${1:-""}

cd "$TRADER_PATH"
source .venv/bin/activate

if [ "$FORCE" = "--force" ]; then
    python -c "
from dotenv import load_dotenv
load_dotenv('$TRADER_PATH/.env')
import runner
runner.run(force=True)
"
else
    python -c "
from dotenv import load_dotenv
load_dotenv('$TRADER_PATH/.env')
import runner
runner.run()
"
fi
