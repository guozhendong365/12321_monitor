"""
12321 投诉量监控 — 定时任务调度器
使用内置 schedule 库，无需额外配置 Windows 任务计划
运行: python scheduler.py
"""

import subprocess
import sys
import time
import logging
from pathlib import Path

try:
    import schedule
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule

BASE_DIR   = Path(__file__).parent
SCRAPER    = BASE_DIR / "scraper.py"
LOG_FILE   = BASE_DIR / "logs" / "scheduler.log"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def job():
    logger.info("触发抓取任务...")
    result = subprocess.run(
        [sys.executable, str(SCRAPER), "--once"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        logger.info("抓取成功")
    else:
        logger.error(f"抓取失败: {result.stderr}")


# 每小时的第 0 分钟执行（即整点执行）
for h in range(24):
    schedule.every().day.at(f"{h:02d}:00").do(job)

logger.info("📅 调度器启动，每小时整点自动抓取")

# 启动时先立刻执行一次
job()

while True:
    schedule.run_pending()
    time.sleep(30)
