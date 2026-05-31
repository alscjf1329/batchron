module.exports = {
  apps: [
    {
      name: "batchron",
      script: "main.py",
      interpreter: ".venv/bin/python",   // Linux venv Python
      args: "--tick 10",                 // 10초마다 cron 체크
      cwd: "/home/사용자명/project/batchron",  // ← 실제 경로로 변경

      // 재시작 정책
      autorestart: true,          // 크래시 시 자동 재시작
      watch: false,               // 파일 변경 감지 OFF
      max_restarts: 10,           // 최대 재시작 횟수
      restart_delay: 5000,        // 재시작 전 대기 5초

      // 로그
      out_file: "logs/pm2_out.log",
      error_file: "logs/pm2_err.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true,

      // 환경변수
      env: {
        PYTHONUNBUFFERED: "1",     // print() 즉시 출력 (버퍼링 없음)
        PYTHONIOENCODING: "utf-8",
      },
    },
  ],
};
