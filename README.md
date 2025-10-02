# 🤖 HuggingFace Daily Papers Bot# 🤖## ✨ 功能特性



自动爬取 HuggingFace 每日热门论文并推送到 Telegram 频道的机器人。- 🕷️ 使用 BeautifulSoup4 爬取 HuggingFace Papers 页面

- 📝 获取论文标题、作者、完整摘要和缩略图

## ✨ 功能特性- 🔗 自动提取 arXiv URL

- 💾 智能缓存机制，基于 Parquet 存储避免重复推送

- 🕷️ 使用 BeautifulSoup4 爬取 HuggingFace Papers 页面- 💿 Parquet 格式本地存储，支持增量更新和去重

- 📝 获取论文标题、作者、完整摘要和缩略图- ☁️ 自动月度归档并上传到 S3（可选）

- 🔗 自动提取 arXiv 和 GitHub 链接- 🔧 使用 OpenDAL 统一文件访问接口

- 📊 获取 GitHub Stars 和 HuggingFace Upvotes 统计数据- 🌐 可选 AI 翻译功能（支持多语言摘要）

- 💾 智能缓存机制，基于 Parquet 存储避免重复推送- ⏱️ 定时检查（可配置间隔时间）

- 💿 Parquet 格式本地存储，支持增量更新和去重- 📢 自动推送新论文到 Telegram 频道

- ☁️ 自动月度归档并上传到 S3（可选）- 🖼️ 支持图片预览 Daily Papers Bot

- 🔧 使用 OpenDAL 统一文件访问接口

- 🌐 可选 AI 翻译功能（支持多语言摘要）自动爬取 HuggingFace 每日热门论文并推送到 Telegram 频道的机器人。

- ⏱️ 定时检查（可配置间隔时间）

- 📢 自动推送新论文到 Telegram 频道## ✨ 功能特性

- 🖼️ 支持图片预览

- 🕷️ 使用 BeautifulSoup4 爬取 HuggingFace Papers 页面

## 📁 项目结构- 📝 获取论文标题、作者、完整摘要和缩略图

- � 自动提取 arXiv URL

```- �💾 智能缓存机制，避免重复推送

telegram-huggingface-daily-papers-bot/- 💿 Parquet 格式本地存储，支持长期数据保存

├── hf.py                    # 爬虫模块（核心）- ☁️ 自动月度归档并上传到 S3（可选）

├── cache.py                 # 缓存管理- 🔧 使用 OpenDAL 统一文件访问接口

├── storage.py               # Parquet 存储 + S3 上传- ⏱️ 定时检查（可配置间隔时间）

├── main.py                  # Telegram Bot 主程序- 📢 自动推送新论文到 Telegram 频道

├── quickstart.fish          # 快速启动脚本- 🖼️ 支持图片预览

├── start.fish               # 启动脚本

├── pyproject.toml           # 项目依赖配置## 📁 项目结构

├── Dockerfile               # Docker 镜像

├── docker-compose.yml       # Docker Compose 配置```

├── docker-bake.hcl          # 多平台构建配置telegram-huggingface-daily-papers-bot/

├── .env.example             # 环境变量示例├── hf.py                    # 爬虫模块（核心）

├── README.md                # 项目说明（本文件）├── cache.py                 # 缓存管理

├── docs/                    # 文档目录├── storage.py               # Parquet 存储 + S3 上传

│   ├── README.md            # 文档索引├── main.py                  # Telegram Bot 主程序

│   ├── USAGE.md             # 详细使用指南├── quickstart.fish          # 快速启动脚本

│   ├── DOCKER.md            # Docker 部署指南├── start.fish               # 启动脚本

│   ├── PROJECT_SUMMARY.md   # 项目总结├── pyproject.toml           # 项目依赖配置

│   ├── CACHE_STORAGE.md     # 缓存和存储集成说明├── Dockerfile               # Docker 镜像

│   └── GITHUB_STATS.md      # GitHub 统计功能说明├── docker-compose.yml       # Docker Compose 配置

├── tests/                   # 测试脚本目录├── docker-bake.hcl          # 多平台构建配置

│   ├── README.md            # 测试说明├── .env.example             # 环境变量示例

│   ├── test.fish            # 完整测试脚本├── README.md                # 项目说明（本文件）

│   ├── test_arxiv.py        # arXiv URL 测试├── docs/                    # 文档目录

│   ├── test_github_stats.py # GitHub 统计测试│   ├── README.md            # 文档索引

│   ├── test_cache_storage.py # 缓存存储测试│   ├── USAGE.md             # 详细使用指南

│   ├── verify_data.py       # 数据验证脚本│   ├── DOCKER.md            # Docker 部署指南

│   ├── debug_html.py        # HTML 调试工具│   └── PROJECT_SUMMARY.md   # 项目总结

│   └── debug_upvotes.py     # Upvotes 调试工具├── tests/                   # 测试脚本目录

└── data/                    # 数据存储目录（自动创建）│   ├── README.md            # 测试说明

    └── YYYY/│   ├── test.fish            # 完整测试脚本

        └── MM/│   ├── test_arxiv.py        # arXiv URL 测试

            └── papers_YYYY-MM-DD.parquet│   ├── verify_data.py       # 数据验证脚本

```│   └── debug_html.py        # HTML 调试工具

└── data/                    # 数据存储目录（自动创建）

## 🚀 快速开始    └── YYYY/

        └── MM/

### 1. 克隆项目            └── papers_YYYY-MM-DD.parquet

```

```bash

git clone <your-repo-url>## 🚀 快速开始

cd telegram-huggingface-daily-papers-bot

```### 1. 克隆项目



### 2. 安装依赖```bash

git clone <your-repo-url>

使用 uv（推荐）：cd telegram-huggingface-daily-papers-bot

```bash```

uv sync

```### 2. 安装依赖



或使用 pip：使用 uv（推荐）：

```bash```bash

pip install -e .uv sync

``````



### 3. 配置环境变量或使用 pip：

```bash

复制示例配置文件：pip install -r requirements.txt

```bash```

cp .env.example .env

```### 3. 配置环境变量



编辑 `.env` 文件，填入你的配置：复制示例配置文件：

```env```bash

# Telegram 配置cp .env.example .env

TELEGRAM_BOT_TOKEN=your_bot_token_here```

TELEGRAM_CHANNEL_ID=@your_channel

CHECK_INTERVAL=3600编辑 `.env` 文件，填入你的配置：

```bash

# AI 翻译配置（可选）# 从 @BotFather 获取 Bot Token

ENABLE_AI_TRANSLATION=falseTELEGRAM_BOT_TOKEN=your_bot_token_here

OPENAI_API_KEY=your_openai_key

OPENAI_MODEL=gpt-4o-mini# 你的 Telegram 频道 ID（如 @your_channel）

TRANSLATION_TARGET_LANG=ChineseTELEGRAM_CHANNEL_ID=@your_channel



# S3 存储配置（可选）# 检查间隔（秒），默认 3600 秒（1小时）

S3_BUCKET=your-bucketCHECK_INTERVAL=3600

S3_ENDPOINT=https://s3.amazonaws.com```

S3_ACCESS_KEY=your_access_key

S3_SECRET_KEY=your_secret_key### 4. 运行 Bot

```

```bash

### 4. 运行 Bot# 使用 uv

uv run python main.py

```bash

# 使用 uv# 或直接运行

uv run python main.pypython main.py

```

# 或直接运行

python main.py## 📋 如何获取 Telegram 配置

```

### 获取 Bot Token

## 📊 数据字段说明

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)

每篇论文包含以下信息：2. 发送 `/newbot` 创建新机器人

3. 按提示设置机器人名称

| 字段 | 类型 | 说明 | 示例 |4. 获得 Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

|------|------|------|------|

| `paper_id` | string | 唯一标识符 | `2509.24002` |### 获取频道 ID

| `title` | string | 论文标题 | `MCPMark: A Benchmark...` |

| `authors` | list[string] | 作者列表 | `["Author1", "Author2"]` |1. 创建一个 Telegram 频道

| `abstract` | string | 论文摘要 | `This paper presents...` |2. 将你的 Bot 添加为频道管理员

| `url` | string | HuggingFace URL | `https://huggingface.co/papers/...` |3. 使用频道用户名（如 `@your_channel`）或数字 ID

| `arxiv_url` | string | ArXiv URL | `https://arxiv.org/abs/...` |

| `github_url` | string | GitHub 仓库链接 | `https://github.com/...` |### 获取数字频道 ID（可选）

| `github_stars` | int | GitHub stars 数 | `184` |

| `hf_upvotes` | int | HuggingFace upvotes | `118` |```bash

| `hero_image` | string | 缩略图 URL | `https://cdn-thumbnails...` |# 在频道发送一条消息，然后访问：

| `collected_at` | string | 收集时间 | `2025-10-02T12:34:56` |https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

```

## 📋 Telegram 消息格式

## 🗂️ 项目结构

```

*Paper Title*```

.

👥 *Authors:* Author1, Author2, Author3, ...├── main.py          # 主程序 - Bot 逻辑和定时任务

├── hf.py            # HuggingFace 爬虫模块

📄 *Abstract:* Paper abstract content...├── cache.py         # 缓存管理模块（避免重复推送）

├── storage.py       # 数据持久化模块（Parquet + S3）

📊 👍 118 upvotes | ⭐ 184 stars├── pyproject.toml   # 项目配置和依赖

├── .env.example     # 环境变量示例

🔗 *Read More：* HuggingFace | ArXiv | GitHub├── data/            # 本地数据存储目录

```│   └── YYYY/        # 年份目录

│       └── MM/      # 月份目录

## 🔧 配置选项│           ├── papers_YYYY-MM-DD.parquet  # 每日数据

│           └── papers_YYYY-MM_merged.parquet  # 月度合并数据

### Telegram 配置└── README.md        # 项目说明

```

| 环境变量 | 说明 | 默认值 |

|---------|------|--------|## 🔧 配置选项

| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（必填） | - |

| `TELEGRAM_CHANNEL_ID` | Telegram 频道 ID（必填） | - || 环境变量 | 说明 | 默认值 |

| `CHECK_INTERVAL` | 检查间隔（秒） | 3600 ||---------|------|--------|

| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 必填 |

| `TELEGRAM_CHANNEL_ID` | Telegram 频道 ID | 必填 |
| `CHECK_INTERVAL` | 检查间隔（秒） | 3600 |

### AI 功能配置（翻译 + 智能总结）

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `ENABLE_AI_TRANSLATION` | 是否启用 AI 功能 | false |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `OPENAI_BASE_URL` | OpenAI API 端点 | https://api.openai.com/v1 |
| `OPENAI_MODEL` | 使用的模型 | gpt-4o-mini |
| `TRANSLATION_TARGET_LANG` | 目标语言 | Chinese |

**AI 功能包括**：
- 🤖 **智能摘要总结**：将长摘要总结到合适长度（保留关键信息）
- 🌐 **多语言翻译**：翻译为目标语言
- ✨ **自动适配**：带图片消息自动总结到更短（~300字符），纯文本可以更长（~600字符）

### 数据存储配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DATA_DIR` | 数据目录路径 | `data` |
| `ARCHIVE_DIR` | 归档目录路径 | `data/archive` |

**注意**: 归档目录应独立于数据目录，不要设置为数据目录的子目录。

## 💾 数据存储说明

### 本地存储

Bot 会将每天采集的论文数据保存为 Parquet 格式：

- 路径：`data/YYYY/MM/YYYYMMDD.parquet`
- 格式：高效的列式存储，支持快速查询和分析
- 压缩：Snappy（58 篇论文 ≈ 0.07 MB）
- 字段：paper_id, title, authors, abstract, url, hero_image, arxiv_url, github_url, github_stars, hf_upvotes, collected_at
- 特性：支持增量更新和自动去重

**示例**: `data/2025/10/20251002.parquet`

### 月度归档

每月 1 号自动执行上个月的数据归档：

1. 合并该月所有每日数据
2. 去重（基于 paper_id）
3. 生成月度文件：`YYYYMM.parquet`
4. 保存到归档目录

归档使用 OpenDAL 文件系统存储，便于后续扩展到云存储。

**示例**: `data/archive/2025/202510.parquet`

### 缓存机制

- 文件：`papers_cache.json`
- 初始化：启动时从 Parquet 文件加载所有历史论文 ID

- 更新：批量更新，减少 I/O 操作- Amazon S3

- 恢复：缓存丢失时自动从 Parquet 文件恢复- MinIO

- Cloudflare R2

### 月度归档- 阿里云 OSS

- 腾讯云 COS

每月 1 号自动执行上个月的归档：- 等其他 S3 兼容存储

1. 合并该月所有每日数据

2. 去重（基于 paper_id）### 查看存储统计

3. 生成月度文件：`papers_YYYY-MM_merged.parquet`

4. 上传到 S3（如果配置）```bash

python -c "from storage import PaperStorage; s = PaperStorage(); print(s.get_statistics())"

## 🛠️ 开发测试```



### 测试爬虫功能## �📦 依赖包



```bash- `requests` - HTTP 请求

# 测试 ArXiv URL 提取- `beautifulsoup4` - HTML 解析

python tests/test_arxiv.py- `pydantic` - 数据验证

- `python-telegram-bot` - Telegram Bot API

# 测试 GitHub 链接和统计数据- `pandas` - 数据处理

python tests/test_github_stats.py- `pyarrow` - Parquet 文件读写

- `opendal` - 统一文件访问接口

# 测试缓存和存储集成

python tests/test_cache_storage.py## 🐳 Docker 部署（可选）

```

```bash

### 验证数据# 构建镜像

docker build -t hf-papers-bot .

```bash

# 验证保存的 Parquet 数据# 运行容器

python tests/verify_data.pydocker run -d \

```  -e TELEGRAM_BOT_TOKEN=your_token \

  -e TELEGRAM_CHANNEL_ID=@your_channel \

### 调试工具  -e CHECK_INTERVAL=3600 \

  -v $(pwd)/papers_cache.json:/app/papers_cache.json \

```bash  hf-papers-bot

# 调试 HTML 结构```

python tests/debug_html.py

## 📝 缓存说明

# 调试 Upvotes 提取

python tests/debug_upvotes.pyBot 会在项目目录下创建 `papers_cache.json` 文件，用于记录已推送的论文 ID。

```

- 首次运行会推送当天所有论文

## 📚 详细文档- 后续运行只推送新增论文

- 如需重新推送所有论文，删除缓存文件即可

- [CACHE_STORAGE.md](docs/CACHE_STORAGE.md) - 缓存和存储集成原理
- [FILESYSTEM_STORAGE.md](docs/FILESYSTEM_STORAGE.md) - 文件系统存储说明和扩展性
- [AI_SUMMARIZATION.md](docs/AI_SUMMARIZATION.md) - AI 智能摘要总结功能
- [GITHUB_STATS.md](docs/GITHUB_STATS.md) - GitHub 统计功能详解
- [TELEGRAM_CHANNEL_SETUP.md](docs/TELEGRAM_CHANNEL_SETUP.md) - Telegram 频道配置完整指南
- [MARKDOWN_V2_FIX.md](docs/MARKDOWN_V2_FIX.md) - Markdown V2 转义问题修复
- [MESSAGE_LENGTH_LIMIT.md](docs/MESSAGE_LENGTH_LIMIT.md) - 消息长度限制处理
- [USAGE.md](docs/USAGE.md) - 详细使用指南
- [DOCKER.md](docs/DOCKER.md) - Docker 部署指南
- [PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) - 项目总结

## 🛠️ 开发测试

测试爬虫功能：

```bash

python tests/test_arxiv.py

## 🐳 Docker 部署```



```bash测试完整流程：

# 构建镜像```bash

docker build -t hf-papers-bot ../tests/test.fish

```

# 使用 docker-compose

docker-compose up -d验证保存的数据：

```bash

# 多平台构建python tests/verify_data.py

docker buildx bake --push```

```

手动归档指定月份：

详见 [DOCKER.md](docs/DOCKER.md)```python

from storage import PaperStorage

## 📈 数据分析示例storage = PaperStorage()

storage.archive_month(2025, 10)  # 归档 2025 年 10 月

```python```

import pandas as pd

## 📚 文档

# 读取数据

df = pd.read_parquet('data/2025/10/papers_2025-10-02.parquet')- [使用指南](docs/USAGE.md) - 详细的使用说明和示例

- [Docker 部署](docs/DOCKER.md) - Docker 部署完整指南

# 按 upvotes 排序- [项目总结](docs/PROJECT_SUMMARY.md) - 项目完成情况和技术细节

top_papers = df.nlargest(10, 'hf_upvotes')[['title', 'hf_upvotes', 'github_stars']]

## 📄 许可证

# 统计有代码的论文比例

has_github = (df['github_url'].notna()).sum() / len(df) * 100MIT License

print(f"有 GitHub 代码的论文: {has_github:.1f}%")

## 🤝 贡献

# upvotes 和 stars 的相关性

correlation = df[['hf_upvotes', 'github_stars']].corr()欢迎提交 Issue 和 Pull Request！

print(correlation)
```

## 📦 依赖包

- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析
- `pydantic` - 数据验证
- `python-telegram-bot` - Telegram Bot API
- `pandas` - 数据处理
- `pyarrow` - Parquet 文件读写
- `opendal` - 统一文件访问接口
- `openai` - AI 翻译（可选）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔗 相关链接

- [HuggingFace Papers](https://huggingface.co/papers)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenDAL](https://opendal.apache.org/)
- [Parquet Format](https://parquet.apache.org/)
