# YouTube Trending Weekly Report Workflow

## Objective
Gather trending videos from YouTube India and send a crisp weekly summary via Telegram.
Supports filtering for AI/ML and Data Analytics content with usage tracking.

## Required Inputs
- Telegram bot token (in `.env`)
- Telegram chat ID (in `.env`)
- YouTube API key (optional, in `.env`)

## Expected Outputs
- JSON file with raw trending data (`.tmp/trending_raw.json`)
- AI-generated summary (`.tmp/ai_summary.txt`)
- Formatted text report (`.tmp/trending_formatted.json`)
- Telegram message delivered to your chat
- Analytics tracking (`.tmp/analytics.json`)

---

## Step 1: Scrape YouTube Trending

**Tool:** `tools/scrape_youtube_trending.py`

### For General Trending:
```bash
python tools/scrape_youtube_trending.py 20
```

### For AI/Data Analytics Only:
```bash
python tools/scrape_youtube_trending.py 5 --ai
```

- Fetches trending videos from YouTube India
- With `--ai` flag: Filters for AI/ML and Data Analytics topics
- Extracts: title, channel name, view count, video URL
- Saves to `.tmp/trending_raw.json`
- Creates `.tmp/ai_mode.flag` when running in AI mode

**Note:** Use `--test` flag for sample data when APIs are unavailable:
```bash
python tools/scrape_youtube_trending.py 5 --ai --test
```

---

## Step 2: Generate AI Summary

**Tool:** `tools/generate_video_summary.py`

```bash
python tools/generate_video_summary.py
```

- Uses local Claude Code to analyze trending videos
- Generates a crisp 2-3 sentence summary of trends
- Saves to `.tmp/ai_summary.txt`

---

## Step 3: Format Report

**Tool:** `tools/format_trending_report.py`

```bash
python tools/format_trending_report.py 5
```

- Converts JSON to crisp WhatsApp/Telegram-friendly text
- Includes "Best Resources - AI Study & Data Analytics" header when in AI mode
- Includes AI summary at the top
- Saves to `.tmp/trending_formatted.json`

---

## Step 4: Send via Telegram

**Tool:** `tools/send_telegram_message.py`

```bash
python tools/send_telegram_message.py
```

- Sends formatted messages to your Telegram
- Reads credentials from `.env`
- **Automatically records analytics** including:
  - Telegram username
  - Date and time of message
  - Number of messages sent
  - Video count in report

---

## Step 5: View Analytics

**Tool:** `tools/telegram_analytics.py`

### View Full Analytics:
```bash
python tools/telegram_analytics.py
```

### View Summary:
```bash
python tools/telegram_analytics.py --summary
```

---

## Complete Workflows

### For AI/Data Analytics Top 5:
```bash
python tools/scrape_youtube_trending.py 5 --ai --test && \
python tools/generate_video_summary.py && \
python tools/format_trending_report.py 5 && \
python tools/send_telegram_message.py
```

### For General Trending:
```bash
python tools/scrape_youtube_trending.py 20 --test && \
python tools/generate_video_summary.py && \
python tools/format_trending_report.py 20 && \
python tools/send_telegram_message.py
```

---

## Configuration (.env)

Create a `.env` file with your API keys:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**Security:** `.env` is in `.gitignore` - never committed to git.

---

## Scheduling (Optional)

To automate weekly reports, use Claude Code's `/schedule` skill:
- Set cron: Every Sunday at 9 AM IST
- Command: The complete workflow above

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "chat not found" | Start the bot in Telegram first |
| No videos scraped | Use `--test` for sample data |
| API rate limited | Wait and retry |
| No AI videos found | Try increasing limit or use `--test` |

---

## Files Created

| File | Purpose |
|------|---------|
| `tools/scrape_youtube_trending.py` | Scrapes YouTube trending (supports --ai flag) |
| `tools/generate_video_summary.py` | AI summary via Claude Code |
| `tools/format_trending_report.py` | Formats for Telegram |
| `tools/send_telegram_message.py` | Sends to Telegram + records analytics |
| `tools/telegram_analytics.py` | Tracks usage analytics |
| `workflows/youtube_weekly_report.md` | This workflow doc |
| `.env` | Your bot credentials |
| `.tmp/analytics.json` | Usage analytics data |

---

## Analytics Tracked

The system automatically records:
- **User info**: Telegram username, chat ID
- **Timing**: Date and time of each report sent
- **Usage**: Number of messages and videos per report
- **History**: First/last interaction, daily stats
- **Per-user stats**: Individual report counts