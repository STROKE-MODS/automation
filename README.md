# YouTube AI Digest

Automated weekly reports of AI/ML/Data Science videos delivered to Telegram. Built with a modular architecture for extensibility.

## Problem Statement

Staying updated with AI/ML content requires manual searching across YouTube. This project automates:
- Discovering trending AI/ML videos
- Generating AI-powered summaries
- Delivering formatted reports to Telegram
- Running on a weekly schedule (or on-demand)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    YouTube AI Digest                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ Scraper │───▶│ Summary │───▶│ Formatter│───▶│ Notifier│  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│       │             │              │              │         │
│       ▼             ▼              ▼              ▼         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Orchestrator (run.py)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| `src/scrapers/youtube.py` | YouTube Data API + Search API integration |
| `src/formatters/telegram.py` | HTML formatting for Telegram messages |
| `src/notifiers/telegram.py` | Telegram Bot API integration |
| `src/utils/summary.py` | AI-powered video summarization |
| `tools/run.py` | Main orchestrator script |

## Installation

```bash
# Clone the repository
git clone https://github.com/STROKE-MODS/automation.git
cd automation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Add your API keys to `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
YOUTUBE_API_KEY=your_youtube_api_key
ANTHROPIC_API_KEY=your_claude_api_key  # For summaries
```

## Usage

### Local Execution

```bash
# Run full pipeline (scrape → summarize → format → send)
python run.py --ai

# Test mode (uses sample data)
python run.py --ai --test

# Limit number of videos
python run.py --ai -n 10

# Skip specific steps
python run.py --ai --skip-scrape --skip-summary
```

### Individual Steps

```bash
# 1. Scrape AI-related videos
python tools/scrape_youtube_trending.py 5 --ai

# 2. Generate AI summary
python tools/generate_video_summary.py

# 3. Format report
python tools/format_trending_report.py 5

# 4. Send to Telegram
python tools/send_telegram_message.py
```

## Automation

### GitHub Actions (Recommended)

The workflow runs automatically every Sunday at 9:00 AM IST.

**Manual trigger:** Actions → YouTube AI Digest → Run workflow

### Windows Task Scheduler

```bash
# Edit run_weekly.bat path, then add via Task Scheduler
schtasks /create /tn "YouTube AI Digest" /tr "path\to\run_weekly.bat" /sc weekly /d SUN
```

## Project Structure

```
automation/
├── src/                      # Source packages
│   ├── scrapers/             # Data collection
│   ├── formatters/           # Output formatting
│   ├── notifiers/            # Message delivery
│   └── utils/                # Shared utilities
├── tests/                    # Unit tests
├── docs/                     # Documentation
├── tools/                    # CLI entry points
├── workflows/                # SOP documentation
├── .github/workflows/        # CI/CD pipelines
├── requirements.txt          # Python dependencies
├── setup.py                  # Package configuration
├── run.py                    # Main orchestrator
└── README.md                 # This file
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_scraper.py

# With coverage
pytest tests/ --cov=src
```

### Adding New Sources

1. Create scraper in `src/scrapers/`
2. Implement `scrape(limit, **kwargs)` function
3. Add to orchestrator in `run.py`

### Adding New Destinations

1. Create notifier in `src/notifiers/`
2. Implement `send(message)` function
3. Add CLI flag in `run.py`

## Output Examples

### Telegram Message

```
📚 Best Resources - AI Study & Data Analytics
🎯 Top Trending Videos
📅 06 Apr 2026

💡 Summary:
These videos show a massive surge in AI/ML education
content, with creators targeting beginners...

1. How to start AI/ML in 2026 ?
   📺 Apna College • 👁 0
   🔗 https://youtube.com/watch?v=...
2. Machine Learning Engineer Full Course 2026
   📺 Simplilearn • 👁 0
   ...
```

## API Rate Limits

| API | Limit | Notes |
|-----|-------|-------|
| YouTube Data API | 10,000 units/day | Search costs 100 units |
| Telegram Bot API | Unlimited | Rate limited by bot |
| Anthropic API | Based on plan | For summaries |

## Troubleshooting

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | Check YouTube API key |
| `403 Forbidden` | API rate limit exceeded |
| `400 Bad Request` | Invalid parameters |
| Telegram send failed | Verify bot token & chat ID |

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

Built with ❤️ using Python, YouTube Data API, and Claude AI