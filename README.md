# YouTube AI & Data Analytics Weekly Report

Automated YouTube trending reports delivered to Telegram every week. Filters for AI, Machine Learning, and Data Analytics content.

## Features

- 🤖 **AI/ML Filtering** - Automatically filters for AI, Machine Learning, Data Analytics, Python tutorials
- 📊 **Weekly Automation** - Runs every Sunday at 9:00 AM IST via GitHub Actions
- 📱 **Telegram Delivery** - Crisp formatted reports delivered to your Telegram
- 📈 **Analytics Tracking** - Tracks usage (username, date/time, message counts)
- 🔄 **No Laptop Required** - Runs entirely on GitHub's servers

## Quick Start

### Local Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Scrape AI/Data Analytics top 5 videos
python tools/scrape_youtube_trending.py 5 --ai --test

# Generate AI summary
python tools/generate_video_summary.py

# Format report
python tools/format_trending_report.py 5

# Send to Telegram
python tools/send_telegram_message.py
```

### One-liner

```bash
python tools/scrape_youtube_trending.py 5 --ai --test && python tools/generate_video_summary.py && python tools/format_trending_report.py 5 && python tools/send_telegram_message.py
```

## Usage Options

### AI/Data Analytics Mode (Default)
```bash
python tools/scrape_youtube_trending.py 5 --ai
```
Shows: "📚 Best Resources - AI Study & Data Analytics"

### General Trending Mode
```bash
python tools/scrape_youtube_trending.py 20
```
Shows: "📊 YouTube Trending India"

## View Analytics

```bash
# Full analytics
python tools/telegram_analytics.py

# Summary report
python tools/telegram_analytics.py --summary
```

Sample output:
```json
{
  "total_reports_sent": 5,
  "total_messages_sent": 5,
  "unique_users": 1,
  "users": {
    "5170723414": {
      "username": "YourUsername",
      "reports_received": 5
    }
  }
}
```

## Automation (GitHub Actions)

The workflow runs automatically every Sunday at 9:00 AM IST.

### Manual Trigger
Go to: **Actions → YouTube Weekly Report → Run workflow**

## Configuration

Environment variables in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
YOUTUBE_API_KEY=your_youtube_api_key
```

## Project Structure

```
automation/
├── tools/
│   ├── scrape_youtube_trending.py   # Scrape YouTube trending
│   ├── generate_video_summary.py     # AI summary via Claude
│   ├── format_trending_report.py      # Format for Telegram
│   ├── send_telegram_message.py      # Send to Telegram
│   └── telegram_analytics.py         # Track usage analytics
├── workflows/
│   └── youtube_weekly_report.md      # Workflow documentation
├── .github/workflows/
│   └── weekly-report.yml             # GitHub Actions workflow
├── requirements.txt                  # Python dependencies
└── .env                              # API credentials
```

## Sample Report Output

```
📚 Best Resources - AI Study & Data Analytics
🎯 Top Trending Videos
📅 29 Mar 2026

💡 Summary:
These videos cover Python programming for data science...

1. Python for Data Science Full Course 2024
   📺 Code With Harry • 👁 2.5M
   🔗 https://youtube.com/watch?v=...
2. Machine Learning Beginner to Advanced
   📺 Krish Naik • 👁 1.8M
   ...
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No videos found | Use `--test` flag for sample data |
| Telegram send failed | Check bot token and chat ID |
| API rate limited | Wait and retry |

## License

MIT