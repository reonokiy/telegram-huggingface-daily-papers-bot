# HuggingFace Daily Papers Bot

[中文文档](README.zh-CN.md)

A Telegram bot that automatically fetches daily trending papers from HuggingFace and posts them to a Telegram channel.

## Features

- Scrape HuggingFace Papers pages using BeautifulSoup4
- Fetch paper title, authors, full abstract, and thumbnails
- Automatically extract arXiv and GitHub links
- Retrieve GitHub stars and HuggingFace upvotes statistics
- Smart caching mechanism to avoid duplicate posts
- Local storage in Parquet format with incremental updates and deduplication
- Automatic monthly archiving with cloud storage support
- Unified file access interface using OpenDAL
- Optional AI translation and smart summarization
- Scheduled checks with configurable intervals
- Automatic posting of new papers to Telegram channels
- Image preview support

## Project Structure

```
telegram-huggingface-daily-papers-bot/
├── main.py               # Main program - Bot logic and scheduled tasks
├── hf.py                 # HuggingFace scraper module
├── cache.py              # Cache management module
├── storage.py            # Data persistence module (Parquet + cloud storage)
├── config.py             # Configuration management
├── pyproject.toml        # Project configuration and dependencies
├── .env.example          # Environment variable template
├── Dockerfile            # Docker image
├── docker-compose.yml    # Docker Compose configuration
├── docker-bake.hcl       # Multi-platform build configuration
├── data/                 # Local data storage directory
│   └── YYYY/MM/          # Organized by year and month
│       └── YYYYMMDD.parquet
├── docs/                 # Documentation directory
└── tests/                # Test scripts directory
```

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd telegram-huggingface-daily-papers-bot
```

### 2. Install Dependencies

Using uv:

```bash
uv sync
```

### 3. Configure Environment Variables

Copy the example configuration file:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your configuration:

```env
# Get Bot Token from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Your Telegram channel ID (e.g., @your_channel)
TELEGRAM_CHANNEL_ID=@your_channel

# Check interval in seconds (default: 3600 = 1 hour)
CHECK_INTERVAL=3600
```

### 4. Run the Bot

```bash
# Using uv
uv run python main.py

# Or run directly
python main.py
```

## How to Get Telegram Configuration

### Get Bot Token

1. Find [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` to create a new bot
3. Follow the prompts to set the bot name
4. Get the Bot Token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Get Channel ID

1. Create a Telegram channel
2. Add your bot as a channel administrator
3. Use the channel username (e.g., `@your_channel`) or numeric ID

### Get Numeric Channel ID (Optional)

```bash
# Post a message in the channel, then visit:
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

## Configuration Options

### Telegram Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token (required) | - |
| `TELEGRAM_CHANNEL_ID` | Telegram channel ID (required) | - |
| `CHECK_INTERVAL` | Check interval in seconds | 3600 |

### AI Features Configuration (Translation + Smart Summarization)

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `ENABLE_AI_TRANSLATION` | Enable AI features | false |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `OPENAI_BASE_URL` | OpenAI API endpoint | https://api.openai.com/v1 |
| `OPENAI_MODEL` | Model to use | gpt-4o-mini |
| `TRANSLATION_TARGET_LANG` | Target language | Chinese |

AI Features include:
- Smart abstract summarization: Condense long abstracts while preserving key information
- Multi-language translation: Translate to target language
- Auto-adaptation: Shorter summaries for image messages (~300 chars), longer for text-only (~600 chars)

### Data Storage Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DATA_DIR` | Data directory path | `data` |
| `ARCHIVE_DIR` | Archive directory path | `data/archive` |

Note: Archive directory should be independent of data directory.

## Data Storage

### Local Storage

Daily paper data is saved in Parquet format:
- Path: `data/YYYY/MM/YYYYMMDD.parquet`
- Format: Efficient columnar storage for fast queries and analysis
- Compression: Snappy (58 papers ≈ 0.07 MB)
- Fields: paper_id, title, authors, abstract, url, hero_image, arxiv_url, github_url, github_stars, hf_upvotes, collected_at
- Features: Incremental updates and automatic deduplication

Example: `data/2025/10/20251002.parquet`

### Monthly Archiving

Automatic archiving on the 1st of each month:
1. Merge all daily data for the previous month
2. Deduplicate based on paper_id
3. Generate monthly file: `YYYYMM.parquet`
4. Save to archive directory

Example: `data/archive/2025/202510.parquet`

### Cache Mechanism

- File: `papers_cache.json`
- Initialization: Load all historical paper IDs from Parquet files on startup
- Updates: Batch updates to reduce I/O operations
- Recovery: Automatically restore from Parquet files if cache is lost

## Data Fields

Each paper contains the following information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `paper_id` | string | Unique identifier | `2509.24002` |
| `title` | string | Paper title | `MCPMark: A Benchmark...` |
| `authors` | list[string] | Author list | `["Author1", "Author2"]` |
| `abstract` | string | Paper abstract | `This paper presents...` |
| `url` | string | HuggingFace URL | `https://huggingface.co/papers/...` |
| `arxiv_url` | string | ArXiv URL | `https://arxiv.org/abs/...` |
| `github_url` | string | GitHub repository link | `https://github.com/...` |
| `github_stars` | int | GitHub stars count | `184` |
| `hf_upvotes` | int | HuggingFace upvotes | `118` |
| `hero_image` | string | Thumbnail URL | `https://cdn-thumbnails...` |
| `collected_at` | string | Collection timestamp | `2025-10-02T12:34:56` |

## Telegram Message Format

```
*Paper Title*

*Authors:* Author1, Author2, Author3, ...

*Abstract:* Paper abstract content...

118 upvotes | 184 stars

*Read More:* HuggingFace | ArXiv | GitHub
```

## Development Testing

Test scraper functionality:

```bash
python tests/test_arxiv.py
```

Test complete workflow:

```bash
./tests/test.fish
```

Verify saved data:

```bash
python tests/verify_data.py
```

Manual archiving for specific month:

```python
from storage import PaperStorage

storage = PaperStorage()
storage.archive_month(2025, 10)  # Archive October 2025
```

## Docker Deployment (Optional)

```bash
# Build image
docker build -t hf-papers-bot .

# Run container
docker run -d \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHANNEL_ID=@your_channel \
  -e CHECK_INTERVAL=3600 \
  -v $(pwd)/papers_cache.json:/app/papers_cache.json \
  hf-papers-bot
```

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `pydantic` - Data validation
- `python-telegram-bot` - Telegram Bot API
- `pandas` - Data processing
- `pyarrow` - Parquet file operations
- `opendal` - Unified file access interface
- `openai` - AI translation (optional)

## Documentation

- [Usage Guide](docs/USAGE.md) - Detailed usage instructions and examples
- [Docker Deployment](docs/DOCKER.md) - Complete Docker deployment guide
- [Project Summary](docs/PROJECT_SUMMARY.md) - Project completion status and technical details

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Related Links

- [HuggingFace Papers](https://huggingface.co/papers)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenDAL](https://opendal.apache.org/)
- [Parquet Format](https://parquet.apache.org/)
