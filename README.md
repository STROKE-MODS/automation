# YouTube AI Digest

Automated weekly reports of AI/ML/Data Science videos delivered to Telegram. Filter YouTube for relevant content and get formatted newsletters delivered to your phone.

## Overview

**Problem:** Staying updated with AI/ML content requires manually searching YouTube for trending videos. This project automates:
- Discovering trending AI/ML videos via YouTube API
- Generating AI-powered summaries using Claude
- Delivering formatted reports to Telegram
- Running on a weekly schedule (or on-demand)

**Who is this for:**
- Data scientists wanting to stay updated with AI trends
- ML engineers following new tutorials and courses
- Developers learning AI/ML programming
- Anyone wanting curated AI content delivered to Telegram

## Features

- **Smart Filtering** - Uses YouTube Search API to find AI/ML/DS/Trading content (not just trending)
- **AI Summaries** - Generates contextual summaries using Claude API
- **Telegram Delivery** - Beautiful HTML-formatted messages
- **Weekly Automation** - Runs automatically via GitHub Actions or Task Scheduler
- **Analytics** - Tracks reports sent, users, and message counts

## Installation

```bash
# Clone the repository
git clone https://github.com/STROKE-MODS/automation.git
cd automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys:
# - TELEGRAM_BOT_TOKEN: Get from @BotFather on Telegram
# - TELEGRAM_CHAT_ID: Your Telegram chat ID
# - YOUTUBE_API_KEY: Get from Google Cloud Console
# - ANTHROPIC_API_KEY: Get from anthropic.com (optional, for summaries)
```

### 2. Run the Demo

```bash
# See it in action without API keys
python examples/demo.py
```

**Demo Output:**
```
╔════════════════════════════════════════════════════════════╗
║         YouTube AI Digest - Demo                          ║
║         Automated AI/ML Video Newsletter                  ║
╚════════════════════════════════════════════════════════════╝

▶ Step 1: Scrape AI/ML videos (test mode)
Command: python scripts/scrape_youtube_trending.py 3 --test --ai
Scraped 3 trending videos

▶ Step 2: Generate AI summary
Command: python scripts/generate_video_summary.py
Analyzing with Claude...
Done. Summary: These videos cover Python programming...

▶ Step 3: Format for Telegram
Command: python scripts/format_trending_report.py 3
Formatted 3 videos into 1 message(s)
Saved to: .tmp/trending_report.txt

📄 Generated Report:
--- Message 1/1 ---
📚 Best Resources - AI Study & Data Analytics
🎯 Top Trending Videos
📅 07 Apr 2026

💡 Summary:
These videos cover Python programming for data science...

1. Python for Data Science Full Course
   📺 Code With Harry • 👁 2.5M
   🔗 https://youtube.com/watch?v=...
```

### 3. Run with Real Data

```bash
# Full pipeline with AI filtering
python scripts/run.py --ai

# Test mode (sample data)
python scripts/run.py --ai --test

# Custom number of videos
python scripts/run.py --ai -n 10
```

## Usage

### Command Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `-n, --limit` | Number of videos | 5 |
| `--ai` | Filter for AI/ML content | No |
| `--test` | Use test data | No |
| `--force` | Skip duplicate check | No |
| `--skip-scrape` | Skip scraping | No |
| `--skip-summary` | Skip AI summary | No |
| `--skip-format` | Skip formatting | No |
| `--skip-send` | Skip sending | No |

### Individual Steps

```bash
# 1. Scrape AI-related videos
python scripts/scrape_youtube_trending.py 5 --ai

# 2. Generate AI summary
python scripts/generate_video_summary.py

# 3. Format report
python scripts/format_trending_report.py 5

# 4. Send to Telegram
python scripts/send_telegram_message.py
```

## Project Structure

```
youtube-ai-digest/
├── src/                      # Core library modules
│   ├── scrapers/             # Data collection (future)
│   ├── formatters/           # Output formatting (future)
│   ├── notifiers/            # Message delivery (future)
│   └── utils/                # Shared utilities (future)
├── scripts/                  # CLI entry points
│   ├── run.py               # Main orchestrator
│   ├── scrape_youtube_trending.py
│   ├── generate_video_summary.py
│   ├── format_trending_report.py
│   ├── send_telegram_message.py
│   └── telegram_analytics.py
├── examples/                 # Demo and example scripts
│   └── demo.py
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── .github/workflows/        # CI/CD pipelines
├── requirements.txt          # Python dependencies
├── setup.py                 # Package configuration
├── .env.example            # Configuration template
└── README.md                # This file
```

## Automation

### GitHub Actions (Recommended)

The workflow runs automatically every Sunday at 9:00 AM IST.

```yaml
# See .github/workflows/weekly-report.yml
```

**Manual trigger:** Actions → YouTube AI Digest → Run workflow

### Windows Task Scheduler

```cmd
schtasks /create /tn "YouTube AI Digest" /tr "path\to\run_weekly.bat" /sc weekly /d SUN
```

### Python Schedule

```python
import schedule
import time

schedule.every().sunday.at("09:00").do(lambda: os.system("python scripts/run.py --ai"))

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | Your Telegram chat ID |
| `YOUTUBE_API_KEY` | Yes | YouTube Data API key |
| `ANTHROPIC_API_KEY` | No | For AI summaries |

## Example Output

### Telegram Message

```
📚 Best Resources - AI Study & Data Analytics
🎯 Top Trending Videos
📅 07 Apr 2026

💡 Summary:
These videos show a massive surge in AI/ML education
content, with creators targeting beginners with getting-started
guides, concept explanations, and full courses.

1. How to start AI/ML in 2026 ?
   📺 Apna College • 👁 0
   🔗 https://youtube.com/watch?v=8WzSEikpHk8

2. AI, Machine Learning, Deep Learning Explained
   📺 IBM Technology • 👁 0
   🔗 https://youtube.com/watch?v=qYNweeDHiyU

3. Machine Learning Engineer Full Course 2026
   📺 Simplilearn • 👁 0
   🔗 https://youtube.com/watch?v=53mqteI5TS0

✨ End of Report
```

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Adding New Sources

1. Create scraper in `scripts/`
2. Add CLI argument in `run.py`
3. Test with `python scripts/run.py --your-flag`

### Adding New Destinations

1. Create notifier in `scripts/`
2. Add to orchestrator in `run.py`
3. Test locally before pushing

## API Rate Limits

| API | Limit | Notes |
|-----|-------|-------|
| YouTube Data API | 10,000 units/day | Search = 100 units |
| Telegram Bot API | Unlimited | Rate limited per bot |
| Anthropic API | Based on plan | ~$0.003/msg for summaries |

## Troubleshooting

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | Check YouTube API key |
| `403 Forbidden` | API rate limit - wait and retry |
| `400 Bad Request` | Invalid parameters - check API docs |
| Telegram send failed | Verify bot token & chat ID |
| No videos found | Use `--test` flag first |

## License

MIT License - See LICENSE file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

Built with ❤️ using Python, YouTube Data API, and Claude AI