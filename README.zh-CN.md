# HuggingFace 每日论文机器人

[English](README.md)

自动爬取 HuggingFace 每日热门论文并推送到 Telegram 频道的机器人。

## 功能特性

- 使用 BeautifulSoup4 爬取 HuggingFace Papers 页面
- 获取论文标题、作者、完整摘要和缩略图
- 自动提取 arXiv 和 GitHub 链接
- 获取 GitHub Stars 和 HuggingFace Upvotes 统计数据
- 智能缓存机制，避免重复推送
- Parquet 格式本地存储，支持增量更新和去重
- 自动月度归档并支持云存储
- 使用 OpenDAL 统一文件访问接口
- 可选 AI 翻译和智能摘要功能
- 定时检查，可配置间隔时间
- 自动推送新论文到 Telegram 频道
- 支持图片预览

## 项目结构

```
telegram-huggingface-daily-papers-bot/
├── main.py               # 主程序 - Bot 逻辑和定时任务
├── hf.py                 # HuggingFace 爬虫模块
├── cache.py              # 缓存管理模块
├── storage.py            # 数据持久化模块（Parquet + 云存储）
├── config.py             # 配置管理
├── pyproject.toml        # 项目配置和依赖
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker 镜像
├── docker-compose.yml    # Docker Compose 配置
├── docker-bake.hcl       # 多平台构建配置
├── data/                 # 本地数据存储目录
│   └── YYYY/MM/          # 按年月组织
│       └── YYYYMMDD.parquet
├── docs/                 # 文档目录
└── tests/                # 测试脚本目录
```

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd telegram-huggingface-daily-papers-bot
```

### 2. 安装依赖

使用 uv：

```bash
uv sync
```

### 3. 配置环境变量

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
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

## 如何获取 Telegram 配置

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

## 配置选项

### Telegram 配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（必填） | - |
| `TELEGRAM_CHANNEL_ID` | Telegram 频道 ID（必填） | - |
| `CHECK_INTERVAL` | 检查间隔（秒） | 3600 |

### AI 功能配置（翻译 + 智能摘要）

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `ENABLE_AI_TRANSLATION` | 是否启用 AI 功能 | false |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `OPENAI_BASE_URL` | OpenAI API 端点 | https://api.openai.com/v1 |
| `OPENAI_MODEL` | 使用的模型 | gpt-4o-mini |
| `TRANSLATION_TARGET_LANG` | 目标语言 | Chinese |

AI 功能包括：
- 智能摘要总结：将长摘要总结到合适长度（保留关键信息）
- 多语言翻译：翻译为目标语言
- 自动适配：带图片消息自动总结到更短（约 300 字符），纯文本可以更长（约 600 字符）

### 数据存储配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DATA_DIR` | 数据目录路径 | `data` |
| `ARCHIVE_DIR` | 归档目录路径 | `data/archive` |

注意：归档目录应独立于数据目录。

## 数据存储

### 本地存储

每天采集的论文数据保存为 Parquet 格式：
- 路径：`data/YYYY/MM/YYYYMMDD.parquet`
- 格式：高效的列式存储，支持快速查询和分析
- 压缩：Snappy（58 篇论文约 0.07 MB）
- 字段：paper_id, title, authors, abstract, url, hero_image, arxiv_url, github_url, github_stars, hf_upvotes, collected_at
- 特性：支持增量更新和自动去重

示例：`data/2025/10/20251002.parquet`

### 月度归档

每月 1 号自动执行上个月的归档：
1. 合并该月所有每日数据
2. 去重（基于 paper_id）
3. 生成月度文件：`YYYYMM.parquet`
4. 保存到归档目录

示例：`data/archive/2025/202510.parquet`

### 缓存机制

- 文件：`papers_cache.json`
- 初始化：启动时从 Parquet 文件加载所有历史论文 ID
- 更新：批量更新，减少 I/O 操作
- 恢复：缓存丢失时自动从 Parquet 文件恢复

## 数据字段

每篇论文包含以下信息：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `paper_id` | string | 唯一标识符 | `2509.24002` |
| `title` | string | 论文标题 | `MCPMark: A Benchmark...` |
| `authors` | list[string] | 作者列表 | `["Author1", "Author2"]` |
| `abstract` | string | 论文摘要 | `This paper presents...` |
| `url` | string | HuggingFace URL | `https://huggingface.co/papers/...` |
| `arxiv_url` | string | ArXiv URL | `https://arxiv.org/abs/...` |
| `github_url` | string | GitHub 仓库链接 | `https://github.com/...` |
| `github_stars` | int | GitHub stars 数 | `184` |
| `hf_upvotes` | int | HuggingFace upvotes | `118` |
| `hero_image` | string | 缩略图 URL | `https://cdn-thumbnails...` |
| `collected_at` | string | 收集时间 | `2025-10-02T12:34:56` |

## Telegram 消息格式

```
*论文标题*

*Authors:* Author1, Author2, Author3, ...

*Abstract:* 论文摘要内容...

118 upvotes | 184 stars

*Read More:* HuggingFace | ArXiv | GitHub
```

## 开发测试

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

## Docker 部署（可选）

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

## 依赖包

- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析
- `pydantic` - 数据验证
- `python-telegram-bot` - Telegram Bot API
- `pandas` - 数据处理
- `pyarrow` - Parquet 文件操作
- `opendal` - 统一文件访问接口
- `openai` - AI 翻译（可选）

## 文档

- [使用指南](docs/USAGE.md) - 详细的使用说明和示例
- [Docker 部署](docs/DOCKER.md) - Docker 部署完整指南
- [项目总结](docs/PROJECT_SUMMARY.md) - 项目完成情况和技术细节

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [HuggingFace Papers](https://huggingface.co/papers)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenDAL](https://opendal.apache.org/)
- [Parquet Format](https://parquet.apache.org/)
