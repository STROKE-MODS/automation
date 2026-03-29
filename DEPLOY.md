# Railway Deployment Guide

## Quick Deploy Steps:

1. **Push to GitHub** - Commit all files except `.tmp/` and `.env`
2. **Create Railway project**: https://railway.app/new
3. **Connect GitHub repo**
4. **Add Environment Variables** in Railway dashboard:
   - `TELEGRAM_BOT_TOKEN` = 8689535430:AAHxrjkiccCLk6AXWzUsywneBzuc0UTovBI
   - `TELEGRAM_CHAT_ID` = 5170723414
   - `YOUTUBE_API_KEY` = AIzaSyBP1BKoqruF9mpHO2JzVoNj3VfKfevlrl0

5. **Deploy** - Click Deploy

## Set Weekly Schedule:

After deploying, go to your project in Railway:
- **Settings** → **Cron Jobs** → **New Cron Job**
- **Command**: `python tools/scrape_youtube_trending.py 5 --ai && python tools.generate_video_summary.py && python tools.format_trending_report.py 5 && python tools.send_telegram_message.py`
- **Schedule**: `0 9 * * 0` (Every Sunday 9 AM IST)
- **Timezone**: Asia/Kolkata

## Files to Commit to GitHub:

```
├── tools/
│   ├── scrape_youtube_trending.py
│   ├── generate_video_summary.py
│   ├── format_trending_report.py
│   ├── send_telegram_message.py
│   └── telegram_analytics.py
├── workflows/
│   └── youtube_weekly_report.md
├── .gitignore
├── CLAUDE.md
├── requirements.txt
├── railway.json
└── run_weekly.bat
```

## DON'T commit:
- `.env` - Add via Railway dashboard instead
- `.tmp/` - Temporary files
- `__pycache__/` - Python cache

## Alternative: Render.com

Similar steps - connect GitHub, add env vars, set cron in dashboard.