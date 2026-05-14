#!/usr/bin/env bash
# -------------------------------------------------------
# batchron 실행 스크립트
# 사용법:
#   ./run.sh               # 기본 실행
#   ./run.sh --tick 10     # 폴링 간격 10초
#   ./run.sh --config custom.yaml
# -------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"

# 가상환경 없으면 생성 후 의존성 설치
if [ ! -d "$VENV_DIR" ]; then
    echo "[batchron] 가상환경 생성 중..."
    python -m venv "$VENV_DIR"
    "$VENV_DIR/Scripts/pip" install -q -r requirements.txt
    echo "[batchron] 의존성 설치 완료"
fi

source "$VENV_DIR/Scripts/activate"

echo "[batchron] 시작 ($(date '+%Y-%m-%d %H:%M:%S'))"
python main.py "$@"
