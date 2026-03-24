"""
创建 Windows 任务计划，开机自动运行 scheduler.py
运行方式: python create_task.py
管理员权限不是必需的（创建用户级任务）
"""

import subprocess
import sys
import io
from pathlib import Path

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ── 配置 ──────────────────────────────────────────────────────────────────────
PROJECT_DIR   = Path(__file__).parent.resolve()
TASK_NAME     = "12321_投诉量监控"
SCHEDULER_PY  = PROJECT_DIR / "scheduler.py"
WORK_DIR      = str(PROJECT_DIR)

# 获取当前 Python 的完整路径
PYTHON_EXE    = sys.executable

# ── 创建任务命令 ─────────────────────────────────────────────────────────────
# 使用 schtasks 命令创建任务
# 触发器：用户登录时自动启动
# 设置：不管是否交互运行、最高权限、不存储密码
task_cmd = [
    "schtasks",
    "/create",
    "/tn", TASK_NAME,
    "/tr", f'"{PYTHON_EXE}" "{SCHEDULER_PY}"',
    "/sc", "onlogon",
    "/ru", "SYSTEM",  # 以系统账户运行，无弹窗
    "/rl", "highest",
    "/f",             # 强制覆盖（若已存在）
    "/np",            # 不存储密码
]

print(f"📋 正在创建任务计划：{TASK_NAME}")
print(f"📍 工作目录：{WORK_DIR}")
print(f"🐍 Python 路径：{PYTHON_EXE}")

try:
    result = subprocess.run(
        task_cmd,
        capture_output=True,
        text=True,
        encoding="gbk",  # Windows 中文环境使用 GBK 编码
        check=True,
    )
    print("\n✅ 任务创建成功！")
    print(f"   任务名称：{TASK_NAME}")
    print("   触发方式：用户登录时自动启动")
    print("\n🔍 查看任务：打开「任务计划程序」(taskschd.msc) 找到 " + TASK_NAME)
    print("\n🗑  删除任务：运行此命令")
    print(f"   schtasks /delete /tn {TASK_NAME} /f")

except subprocess.CalledProcessError as e:
    print(f"\n❌ 任务创建失败，错误码：{e.returncode}")
    print(f"错误详情：\n{e.stderr}")
    sys.exit(1)
