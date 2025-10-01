# 🤖 HuggingFace Daily Papers Bot

自动爬取 HuggingFace 每日热门论文并推送到 Telegram 频道的机器人。

## ✨ 功能特性

- 🕷️ 使用 BeautifulSoup4 爬取 HuggingFace Papers 页面
- 📝 获取论文标题、作者、完整摘要和缩略图
- � 自动提取 arXiv URL
- �💾 智能缓存机制，避免重复推送
- 💿 Parquet 格式本地存储，支持长期数据保存
- ☁️ 自动月度归档并上传到 S3（可选）
- 🔧 使用 OpenDAL 统一文件访问接口
- ⏱️ 定时检查（可配置间隔时间）
- 📢 自动推送新论文到 Telegram 频道
- 🖼️ 支持图片预览

## 📁 项目结构

```
telegram-huggingface-daily-papers-bot/
├── hf.py                    # 爬虫模块（核心）
├── cache.py                 # 缓存管理
├── storage.py               # Parquet 存储 + S3 上传
├── main.py                  # Telegram Bot 主程序
├── quickstart.fish          # 快速启动脚本
├── start.fish               # 启动脚本
├── pyproject.toml           # 项目依赖配置
├── Dockerfile               # Docker 镜像
├── docker-compose.yml       # Docker Compose 配置
├── docker-bake.hcl          # 多平台构建配置
├── .env.example             # 环境变量示例
├── README.md                # 项目说明（本文件）
├── docs/                    # 文档目录
│   ├── README.md            # 文档索引
│   ├── USAGE.md             # 详细使用指南
│   ├── DOCKER.md            # Docker 部署指南
│   └── PROJECT_SUMMARY.md   # 项目总结
├── tests/                   # 测试脚本目录
│   ├── README.md            # 测试说明
│   ├── test.fish            # 完整测试脚本
│   ├── test_arxiv.py        # arXiv URL 测试
│   ├── verify_data.py       # 数据验证脚本
│   └── debug_html.py        # HTML 调试工具
└── data/                    # 数据存储目录（自动创建）
    └── YYYY/
        └── MM/
            └── papers_YYYY-MM-DD.parquet
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd telegram-huggingface-daily-papers-bot
```

### 2. 安装依赖

使用 uv（推荐）：
```bash
uv sync
```

或使用 pip：
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：
```bash
# 从 @BotFather 获取 Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 你的 Telegram 频道 ID（如 @your_channel）
TELEGRAM_CHANNEL_ID=@your_channel

# 检查间隔（秒），默认 3600 秒（1小时）
CHECK_INTERVAL=3600
```

### 4. 运行 Bot

```bash
# 使用 uv
uv run python main.py

# 或直接运行
python main.py
```

## 📋 如何获取 Telegram 配置

### 获取 Bot Token

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 获得 Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 获取频道 ID

1. 创建一个 Telegram 频道
2. 将你的 Bot 添加为频道管理员
3. 使用频道用户名（如 `@your_channel`）或数字 ID

### 获取数字频道 ID（可选）

```bash
# 在频道发送一条消息，然后访问：
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

## 🗂️ 项目结构

```
.
├── main.py          # 主程序 - Bot 逻辑和定时任务
├── hf.py            # HuggingFace 爬虫模块
├── cache.py         # 缓存管理模块（避免重复推送）
├── storage.py       # 数据持久化模块（Parquet + S3）
├── pyproject.toml   # 项目配置和依赖
├── .env.example     # 环境变量示例
├── data/            # 本地数据存储目录
│   └── YYYY/        # 年份目录
│       └── MM/      # 月份目录
│           ├── papers_YYYY-MM-DD.parquet  # 每日数据
│           └── papers_YYYY-MM_merged.parquet  # 月度合并数据
└── README.md        # 项目说明
```

## 🔧 配置选项

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 必填 |
| `TELEGRAM_CHANNEL_ID` | Telegram 频道 ID | 必填 |
| `CHECK_INTERVAL` | 检查间隔（秒） | 3600 |
| `S3_BUCKET` | S3 存储桶名称 | 可选 |
| `S3_ENDPOINT` | S3 端点 URL | 可选 |
| `S3_REGION` | S3 区域 | us-east-1 |
| `S3_ACCESS_KEY` | S3 访问密钥 | 可选 |
| `S3_SECRET_KEY` | S3 秘密密钥 | 可选 |

## � 数据存储说明

### 本地存储

Bot 会将每天采集的论文数据保存为 Parquet 格式：
- 路径：`data/YYYY/MM/papers_YYYY-MM-DD.parquet`
- 格式：高效的列式存储，支持快速查询和分析
- 字段：paper_id, title, authors, abstract, url, hero_image, collected_at

### 月度归档

每月 1 号自动执行上个月的数据归档：
1. 合并该月所有每日数据
2. 去重（基于 paper_id）
3. 生成月度文件：`papers_YYYY-MM_merged.parquet`
4. 如果配置了 S3，自动上传到云存储

### S3 云存储（可选）

配置 S3 后，月度归档会自动上传到：
```
s3://your-bucket/papers/YYYY/MM/papers_YYYY-MM_merged.parquet
```

支持的 S3 兼容服务：
- Amazon S3
- MinIO
- Cloudflare R2
- 阿里云 OSS
- 腾讯云 COS
- 等其他 S3 兼容存储

### 查看存储统计

```bash
python -c "from storage import PaperStorage; s = PaperStorage(); print(s.get_statistics())"
```

## �📦 依赖包

- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析
- `pydantic` - 数据验证
- `python-telegram-bot` - Telegram Bot API
- `pandas` - 数据处理
- `pyarrow` - Parquet 文件读写
- `opendal` - 统一文件访问接口

## 🐳 Docker 部署（可选）

```bash
# 构建镜像
docker build -t hf-papers-bot .

# 运行容器
docker run -d \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHANNEL_ID=@your_channel \
  -e CHECK_INTERVAL=3600 \
  -v $(pwd)/papers_cache.json:/app/papers_cache.json \
  hf-papers-bot
```

## 📝 缓存说明

Bot 会在项目目录下创建 `papers_cache.json` 文件，用于记录已推送的论文 ID。

- 首次运行会推送当天所有论文
- 后续运行只推送新增论文
- 如需重新推送所有论文，删除缓存文件即可

## 🛠️ 开发测试

测试爬虫功能：
```bash
python tests/test_arxiv.py
```

测试完整流程：
```bash
./tests/test.fish
```

验证保存的数据：
```bash
python tests/verify_data.py
```

手动归档指定月份：
```python
from storage import PaperStorage
storage = PaperStorage()
storage.archive_month(2025, 10)  # 归档 2025 年 10 月
```

## 📚 文档

- [使用指南](docs/USAGE.md) - 详细的使用说明和示例
- [Docker 部署](docs/DOCKER.md) - Docker 部署完整指南
- [项目总结](docs/PROJECT_SUMMARY.md) - 项目完成情况和技术细节

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
