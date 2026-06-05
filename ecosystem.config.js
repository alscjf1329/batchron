module.exports = {
  apps: [
    {
      name: "batchron",
      script: "main.py",
      interpreter: ".venv/bin/python",
      args: "--tick 10",
      cwd: "/app/batchron",

      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,

      out_file: "logs/pm2_out.log",
      error_file: "logs/pm2_err.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true,

      env: {
        PYTHONUNBUFFERED: "1",
        PYTHONIOENCODING: "utf-8",
        TRADER_PATH: "/app/auto-trader",
      },
    },
  ],
};
