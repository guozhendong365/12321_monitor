"""
从云端同步数据到本地
运行: python sync_data.py
"""

import json
import requests
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "complaints.json"

# 云端数据 URL（需要替换为你的 GitHub 仓库地址）
CLOUD_URL = "https://raw.githubusercontent.com/你的用户名/12321_monitor/main/data/complaints.json"

def sync():
    print("正在从云端同步数据...")
    try:
        resp = requests.get(CLOUD_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"✅ 同步成功！数据已保存到 {DATA_FILE}")

        # 显示最新数据
        today = sorted(data.keys())[-1]
        count = data[today]["daily_count"]
        print(f"   最新数据：{today} -> {count} 条投诉")

    except Exception as e:
        print(f"❌ 同步失败：{e}")

if __name__ == "__main__":
    sync()
