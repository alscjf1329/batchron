#!/bin/bash
# 한국장 AI 매매 — batchron 또는 수동 실행
# 사용: ./jobs/trade_kr.sh

set -euo pipefail

TRADER_PATH="${TRADER_PATH:-/app/auto-trader}"

cd "$TRADER_PATH"
source .venv/bin/activate

python - <<'EOF'
from dotenv import load_dotenv; load_dotenv()
import runner
runner.run_brain_mode()
EOF
