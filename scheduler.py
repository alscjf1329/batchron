import time
import importlib
import logging
import subprocess
import traceback
from datetime import datetime

import yaml
from croniter import croniter

logger = logging.getLogger(__name__)


class JobRunner:
    def __init__(self, job_cfg: dict):
        self.name = job_cfg["name"]
        self.cron_expr = job_cfg["cron"]
        self.enabled = job_cfg.get("enabled", True)
        self._iter = croniter(self.cron_expr, datetime.now())

        # type 미지정 시 script 키 유무로 자동 판별
        self.type = job_cfg.get("type") or ("shell" if "script" in job_cfg else "python")
        self.script = job_cfg.get("script")
        self.module_path = job_cfg.get("module")
        self.function_name = job_cfg.get("function", "run")

    def next_run(self) -> datetime:
        return self._iter.get_next(datetime)

    def execute(self):
        logger.info(f"[{self.name}] starting")
        try:
            if self.type == "shell":
                self._run_shell()
            else:
                self._run_python()
            logger.info(f"[{self.name}] done")
        except Exception:
            logger.error(f"[{self.name}] failed\n{traceback.format_exc()}")

    def _run_python(self):
        # auto-trader 모듈 캐시 초기화 — 파일 수정 후 재시작 없이 반영
        import sys
        _TRADER_MODULES = {
            "brain", "runner", "factor", "risk", "settings",
            "kis_api", "notify", "config",
            "journal", "journal.logger", "journal.snapshot", "journal.review",
            "strategies", "strategies.base",
        }
        for mod in list(sys.modules.keys()):
            if any(mod == m or mod.startswith(m + ".") for m in _TRADER_MODULES):
                del sys.modules[mod]

        module = importlib.import_module(self.module_path)
        func = getattr(module, self.function_name)
        func()

    def _run_shell(self):
        result = subprocess.run(
            ["bash", self.script],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            logger.info(f"[{self.name}] stdout: {result.stdout.strip()}")
        if result.returncode != 0:
            raise RuntimeError(f"exit code {result.returncode}\n{result.stderr.strip()}")


class Scheduler:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        self.runners: list[JobRunner] = [
            JobRunner(j) for j in cfg.get("jobs", []) if j.get("enabled", True)
        ]

        if not self.runners:
            logger.warning("No enabled jobs found in config.")

    def run_forever(self, tick: int = 30):
        """tick 초마다 실행 대상 잡 확인 후 실행."""
        logger.info(f"Scheduler started — {len(self.runners)} job(s) loaded")
        for r in self.runners:
            logger.info(f"  {r.name:20s} cron={r.cron_expr}  next={r.next_run():%Y-%m-%d %H:%M:%S}")

        # 각 잡의 다음 실행 시각을 미리 계산
        schedule: dict[str, datetime] = {r.name: r.next_run() for r in self.runners}

        while True:
            now = datetime.now().replace(second=0, microsecond=0)
            for runner in self.runners:
                if now >= schedule[runner.name].replace(second=0, microsecond=0):
                    runner.execute()
                    schedule[runner.name] = runner.next_run()
                    logger.info(f"[{runner.name}] next run at {schedule[runner.name]:%Y-%m-%d %H:%M:%S}")
            time.sleep(tick)
