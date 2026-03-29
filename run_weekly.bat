@echo off
cd /d "E:\Himanshu Work\Automation"
python tools/scrape_youtube_trending.py 5 --ai --test
python tools/generate_video_summary.py
python tools/format_trending_report.py 5
python tools/send_telegram_message.py
echo Weekly job completed at %date% %time% >> .tmp/scheduler.log
