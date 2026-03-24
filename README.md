# 12321 投诉量监控

每小时自动抓取 12321.cn 投诉数据，生成 7天/15天/30天 趋势曲线

## 功能

- 📊 数据抓取：每小时自动抓取一次今日投诉量
- 📈 可视化：7天/15天/30天 趋势曲线 + 今日实时走势
- 🚀 自动运行：GitHub Actions 每小时自动抓取（本机关机也能运行）
- 🌐 实时看板：本地查看最新数据

## 使用方式

### 方式一：GitHub Actions 自动抓取（推荐）
- 数据每小时自动更新到云端
- 本地看板自动获取最新数据
- 本机关机不影响数据更新

### 方式二：本地运行
```bash
cd 12321_monitor
python scheduler.py    # 持续运行，每小时自动抓取
python scraper.py --once  # 单次抓取
```

## 查看看板

1. 启动本地服务器：
```bash
cd 12321_monitor
python -m http.server 8765
```

2. 浏览器打开：
```
http://localhost:8765/dashboard.html
```

## 项目结构

```
12321_monitor/
├── scraper.py          # 数据抓取脚本
├── scheduler.py        # 本地调度器
├── dashboard.html      # 可视化看板
├── .github/workflows/  # GitHub Actions 工作流
│   └── scraper.yml
└── data/
    └── complaints.json # 数据存储
```

## 数据源

- 本地数据：`data/complaints.json`
- 云端数据（GitHub Actions）：通过 Raw URL 获取（看板会自动切换）
