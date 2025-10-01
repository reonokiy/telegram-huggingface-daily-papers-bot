# 📚 使用指南

## 项目功能总览

这个项目实现了以下功能：

1. **爬取 HuggingFace 每日论文** - 使用 BeautifulSoup4 爬取完整的论文信息
2. **智能缓存** - 避免重复推送相同的论文
3. **数据持久化** - 使用 Parquet 格式存储每日论文数据
4. **自动归档** - 每月自动将数据打包并上传到 S3
5. **Telegram 推送** - 自动将新论文推送到 Telegram 频道
6. **定时运行** - 可配置的检查间隔

## 文件结构

```
.
├── hf.py              # HuggingFace 爬虫模块
├── cache.py           # 论文缓存管理
├── storage.py         # Parquet 存储 + S3 上传
├── main.py            # Telegram Bot 主程序
├── test.fish          # 测试脚本
├── data/              # 本地数据存储目录
│   └── YYYY/
│       └── MM/
│           └── papers_YYYY-MM-DD.parquet
└── .env               # 环境变量配置
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 必需配置
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel

# 可选配置
CHECK_INTERVAL=3600  # 检查间隔（秒）

# S3 配置（可选，用于自动归档）
S3_BUCKET=hf-papers
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
```

### 3. 获取 Telegram Bot Token

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新 bot
3. 按提示设置名称
4. 获得 Token（类似 `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`）

### 4. 创建 Telegram 频道

1. 在 Telegram 中创建一个新频道
2. 将你的 bot 添加为频道管理员
3. 获取频道 ID（如 `@your_channel`）

### 5. 测试运行

```bash
# 测试爬虫和存储功能
./test.fish

# 单次运行（测试推送）
python main.py --once

# 持续运行
python main.py
```

## 使用示例

### 单独使用爬虫

```python
from datetime import date
from hf import fetch_huggingface_papers

# 获取今天的论文
papers = fetch_huggingface_papers(date.today())

for paper in papers:
    print(f"标题: {paper.title}")
    print(f"作者: {', '.join(paper.authors)}")
    print(f"摘要: {paper.abstract[:100]}...")
    print(f"URL: {paper.url}")
    print("-" * 80)
```

### 使用缓存管理

```python
from cache import PaperCache

cache = PaperCache()

# 检查是否已缓存
if not cache.is_cached(paper_id):
    # 处理新论文
    cache.add(paper_id)

# 查看缓存大小
print(f"已缓存 {cache.size()} 篇论文")
```

### 使用存储模块

```python
from datetime import date
from storage import PaperStorage
from hf import fetch_huggingface_papers

storage = PaperStorage()

# 获取并保存论文
papers = fetch_huggingface_papers(date.today())
storage.save_daily_papers(papers, date.today())

# 月度归档（手动）
storage.archive_month(2025, 9)

# 上传到 S3
storage.upload_to_s3(local_file, "papers/2025/09/archive.parquet")

# 查看统计
stats = storage.get_statistics()
print(stats)
```

## 数据格式

### Parquet 文件结构

每个 Parquet 文件包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| paper_id | string | 论文唯一标识（从 URL 提取） |
| title | string | 论文标题 |
| authors | string | 作者列表（JSON 数组字符串） |
| abstract | string | 完整摘要 |
| url | string | 论文链接 |
| hero_image | string | 缩略图 URL |
| collected_at | string | 采集时间（ISO 格式） |

### 读取 Parquet 文件

```python
import pandas as pd
import json

# 读取单个文件
df = pd.read_parquet("data/2025/10/papers_2025-10-02.parquet")

# 解析作者列表
df['authors_list'] = df['authors'].apply(json.loads)

# 查看数据
print(df[['title', 'authors_list', 'url']])
```

## 自动归档说明

每月第一天，系统会自动：

1. 合并上个月的所有每日 Parquet 文件
2. 去重（基于 paper_id）
3. 生成月度归档文件：`papers_YYYY-MM_merged.parquet`
4. 如果配置了 S3，自动上传到云存储

## 故障排查

### 爬虫问题

**问题：**获取不到论文
- 检查日期格式是否正确
- 确认 HuggingFace 网站是否可访问
- 查看是否有新的页面结构变化

**问题：**摘要为空
- HuggingFace 可能还没有加载详细信息
- 尝试增加请求间隔时间

### Telegram 推送问题

**问题：**推送失败
- 检查 Bot Token 是否正确
- 确认 Bot 是否是频道管理员
- 检查频道 ID 格式（应该是 `@channel_name` 或数字 ID）

**问题：**Markdown 格式错误
- 特殊字符需要转义
- 使用 `ParseMode.MARKDOWN_V2`

### S3 上传问题

**问题：**上传失败
- 检查 S3 凭证是否正确
- 确认 Bucket 是否存在
- 检查权限设置

## 高级配置

### 使用 systemd 服务（Linux）

创建服务文件 `/etc/systemd/system/hf-papers-bot.service`：

```ini
[Unit]
Description=HuggingFace Papers Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/telegram-huggingface-daily-papers-bot
Environment="PATH=/path/to/.venv/bin"
ExecStart=/path/to/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable hf-papers-bot
sudo systemctl start hf-papers-bot
sudo systemctl status hf-papers-bot
```

### 使用 Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev

COPY . .

CMD ["python", "main.py"]
```

构建并运行：

```bash
docker build -t hf-papers-bot .
docker run -d --env-file .env hf-papers-bot
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
