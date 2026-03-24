"""
12321 投诉量数据抓取器
每小时抓取一次，保存每日数据
运行方式: python scraper.py
         python scraper.py --once  (抓取一次就退出，用于测试或 cron 调度)
"""

import re
import json
import time
import argparse
import logging
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── 配置 ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_FILE  = BASE_DIR / "data" / "complaints.json"
LOG_FILE   = BASE_DIR / "logs" / "scraper.log"
TARGET_URL = "https://www.12321.cn/"
INTERVAL   = 3600          # 每隔 3600 秒（1 小时）抓取一次
HEADERS    = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ── 日志配置 ──────────────────────────────────────────────────────────────────
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


# ── 核心函数 ──────────────────────────────────────────────────────────────────
def fetch_count() -> int | None:
    """抓取 12321 网站今日已受理投诉数"""
    try:
        resp = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 策略 1：在所有文本中寻找"今天已受理 XXXX 条投诉"
        text = soup.get_text(separator=" ")
        m = re.search(r"今天已受理\s*([\d,]+)\s*条投诉", text)
        if m:
            count = int(m.group(1).replace(",", ""))
            logger.info(f"抓取成功：今日投诉量 = {count}")
            return count

        # 策略 2：查找包含数字的 <span> / <b> 标签（备用）
        for tag in soup.find_all(["span", "b", "strong", "em"]):
            if re.search(r"今天已受理", tag.get_text()):
                m2 = re.search(r"([\d,]+)", tag.get_text())
                if m2:
                    count = int(m2.group(1).replace(",", ""))
                    logger.info(f"备用策略抓取成功：今日投诉量 = {count}")
                    return count

        logger.warning("未能从页面中解析到投诉数字，请检查页面结构是否变更")
        return None

    except requests.RequestException as e:
        logger.error(f"网络请求失败: {e}")
        return None


def load_data() -> dict:
    """加载历史数据"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("数据文件损坏，重置为空")
    return {}


def save_data(data: dict) -> None:
    """保存数据"""
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def record(data: dict, count: int) -> dict:
    """
    将今日投诉量写入数据结构。
    格式：{ "YYYY-MM-DD": { "daily_count": N, "snapshots": [{"time": "HH:MM", "count": N}, ...] } }
    每天用最后一次快照值作为当天的 daily_count（代表截止当时的累计数）
    """
    today = str(date.today())
    now_time = datetime.now().strftime("%H:%M")

    if today not in data:
        data[today] = {"daily_count": count, "snapshots": []}

    data[today]["snapshots"].append({"time": now_time, "count": count})
    data[today]["daily_count"] = count  # 用最新值覆盖（当天最大值）
    save_data(data)
    logger.info(f"已记录 {today} {now_time} -> {count} 条投诉")
    return data


def run_once() -> bool:
    """执行一次抓取"""
    count = fetch_count()
    if count is not None:
        data = load_data()
        record(data, count)
        return True
    return False


def run_loop():
    """持续循环，每小时抓取一次"""
    logger.info("🟢 12321 投诉量监控启动（每小时抓取一次）")
    while True:
        run_once()
        logger.info(f"下次抓取时间：{INTERVAL // 60} 分钟后")
        time.sleep(INTERVAL)


# ── 入口 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="12321 投诉量抓取器")
    parser.add_argument("--once", action="store_true", help="抓取一次后退出（适合 cron/任务计划）")
    args = parser.parse_args()

    if args.once:
        success = run_once()
        exit(0 if success else 1)
    else:
        run_loop()
