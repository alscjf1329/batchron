# batchron

Python으로 작성된 cron 형식 배치 스케줄러.

## 구조

```
batchron/
├── main.py            # 진입점
├── scheduler.py       # cron 파싱 & 스케줄 루프
├── config.yaml        # 잡 설정
├── requirements.txt
├── run.sh             # 실행 스크립트
├── jobs/
│   ├── hello_job.py   # 예제 잡
│   └── cleanup_job.py # 로그 정리 잡
└── logs/              # 실행 로그 (날짜별 로테이션)
```

## 시작하기

```bash
./run.sh
```

최초 실행 시 `.venv` 가상환경을 자동 생성하고 의존성을 설치합니다.

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--config` | `config.yaml` | 사용할 config 파일 경로 |
| `--tick` | `30` | 잡 확인 폴링 간격 (초) |

```bash
./run.sh --tick 10
./run.sh --config prod.yaml
```

## auto-trader 연동

[auto-trader](../auto-trader)의 한국/미국장 자동매매가 잡으로 등록되어 있습니다.

`.env` 파일에 auto-trader 경로 설정:

```env
TRADER_PATH=C:\Users\SheepDuck\Desktop\project\auto-trader
```

| 잡 | cron | 설명 |
|---|---|---|
| `trade_kr` | `*/15 9-15 * * 1-5` | 한국장 AI 매매 (15분) |
| `trade_us_night` | `*/15 23 * * 1-5` | 미국장 AI 매매 — 23시대 |
| `trade_us_dawn` | `*/15 0-4 * * 2-6` | 미국장 AI 매매 — 새벽 |
| `stop_loss_kr` | `*/3 9-15 * * 1-5` | 한국장 손절 감시 (3분, Claude 없음) |
| `stop_loss_us_night` | `*/3 23 * * 1-5` | 미국장 손절 감시 — 23시대 |
| `stop_loss_us_dawn` | `*/3 0-4 * * 2-6` | 미국장 손절 감시 — 새벽 |

---

## 잡 추가

### Python 잡

`jobs/my_job.py` 생성 후 `run()` 함수 작성:

```python
import logging

logger = logging.getLogger(__name__)

def run():
    logger.info("my_job 실행")
    # 로직 작성
```

`config.yaml` 등록:

```yaml
- name: my_job
  module: jobs.my_job
  function: run
  cron: "0 9 * * 1-5"   # 평일 오전 9시
  enabled: true
```

### Shell 잡

`jobs/my_job.sh` 생성:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "my_job.sh 실행: $(date)"
# 로직 작성
```

`config.yaml` 등록:

```yaml
- name: my_job
  type: shell
  script: jobs/my_job.sh
  cron: "0 9 * * 1-5"   # 평일 오전 9시
  enabled: true
```

> `type` 생략 시 `script` 키가 있으면 shell, `module` 키가 있으면 python으로 자동 판별합니다.

## cron 표현식

```
*  *  *  *  *
│  │  │  │  └── 요일 (0=일 ~ 6=토)
│  │  │  └───── 월 (1-12)
│  │  └──────── 일 (1-31)
│  └─────────── 시 (0-23)
└────────────── 분 (0-59)
```

| 표현식 | 설명 |
|--------|------|
| `*/5 * * * *` | 매 5분 |
| `0 * * * *` | 매 시 정각 |
| `0 9 * * 1-5` | 평일 오전 9시 |
| `0 3 * * *` | 매일 새벽 3시 |
| `0 0 1 * *` | 매월 1일 자정 |

## 로그

`logs/batchron.log` 에 기록되며 30일치 보관됩니다.

```
2026-05-12 09:00:00 [INFO] [hello_job] starting
2026-05-12 09:00:00 [INFO] [hello_job] done
2026-05-12 09:00:00 [INFO] [hello_job] next run at 2026-05-12 09:01:00
```

## 의존성

- [croniter](https://github.com/kiorky/croniter) — cron 표현식 파싱
- [PyYAML](https://pyyaml.org/) — config 파싱
