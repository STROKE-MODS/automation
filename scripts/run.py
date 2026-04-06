#!/usr/bin/env python3
"""
YouTube AI Digest - Unified Script
Automated AI/ML video reports delivered to Telegram.

Usage:
    python run.py --ai              # Full pipeline with AI filtering
    python run.py --ai --test       # Test mode with sample data
    python run.py --ai -n 10        # Custom number of videos
    python run.py                   # General trending (no filter)
"""

import sys
import os
import json
import io
import re
import time
import hashlib
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.tmp/orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Fix Unicode on Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

AI_STRONG_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "data science", "data analytics", "data analysis", "tensorflow",
    "pytorch", "keras", "pandas", "numpy", "scikit-learn", "sklearn",
    "chatgpt", "gpt", "llm", "large language model", "neural network",
    "data engineer", "data scientist", "data engineering", "mlops",
    "autogpt", "copilot", "generative ai", "gen ai", "genai", "computer vision",
    "nlp", "natural language processing", "reinforcement learning",
    "transformer", "hugging face", "huggingface", "langchain",
    "prompt engineering", "rag", "retrieval augmented", "fine tuning",
    "fine-tuning", "openai", "anthropic", "gemini", "claude",
    "stable diffusion", "midjourney", "dall-e", "dalle",
    "trading", "stock market", "forex", "crypto", "binance",
    "options trading", "intraday", "nifty", "sensex", "zerodha",
]

# ============================================================================
# SCRAPER FUNCTIONS
# ============================================================================

def _keyword_match(text: str, keywords: list) -> list:
    """Return keywords that match in text using word boundaries."""
    if not text:
        return []
    text_lower = text.lower()
    matched = []
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            matched.append(keyword)
    return matched


def is_ai_video(title: str, tags: list = None, description: str = None, channel: str = None) -> bool:
    """Check if video is AI/ML/Trading related."""
    tags_text = " ".join(tags) if tags else ""
    desc_text = (description or "")[:300]
    all_text = f"{title} {tags_text} {desc_text}"
    return len(_keyword_match(all_text, AI_STRONG_KEYWORDS)) > 0


def scrape_youtube(limit: int = 5, test_mode: bool = False, ai_only: bool = False) -> list:
    """Scrape YouTube for videos."""
    output_file = Path(".tmp") / "trending_raw.json"
    output_file.parent.mkdir(exist_ok=True)

    videos = []

    if test_mode:
        if ai_only:
            videos = [
                {"title": "Python for Data Science Full Course 2024", "channel": "Code With Harry", "views": "2500000", "video_id": "aitest1", "url": "https://youtube.com/watch?v=aitest1"},
                {"title": "Machine Learning Beginner to Advanced", "channel": "Krish Naik", "views": "1800000", "video_id": "aitest2", "url": "https://youtube.com/watch?v=aitest2"},
                {"title": "ChatGPT Complete Guide for Beginners", "channel": "TechWorld With Nana", "views": "3200000", "video_id": "aitest3", "url": "https://youtube.com/watch?v=aitest3"},
                {"title": "Pandas Python Data Analysis Tutorial", "channel": "Python Programmer", "views": "950000", "video_id": "aitest4", "url": "https://youtube.com/watch?v=aitest4"},
                {"title": "Deep Learning Neural Networks Explained", "channel": "3Blue1Brown", "views": "4500000", "video_id": "aitest5", "url": "https://youtube.com/watch?v=aitest5"},
            ][:limit]
        else:
            videos = [
                {"title": "Emergency Alert: Major News Event", "channel": "TV9 India", "views": "15000000", "video_id": "sample1", "url": "https://youtube.com/watch?v=sample1"},
                {"title": "Bollywood Hit Song 2024", "channel": "T-Series", "views": "25000000", "video_id": "sample2", "url": "https://youtube.com/watch?v=sample2"},
                {"title": "Cricket Match Highlights", "channel": "Star Sports", "views": "8000000", "video_id": "sample3", "url": "https://youtube.com/watch?v=sample3"},
            ][:limit]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2)
        logger.info(f"Test mode: Scraped {len(videos)} videos")
        return videos

    # Real API mode
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.warning("No YouTube API key - using test mode")
        return scrape_youtube(limit, test_mode=True, ai_only=ai_only)

    videos = []

    if ai_only:
        # Use search API for AI content
        search_queries = [
            "AI machine learning tutorial", "data science tutorial",
            "python programming tutorial", "chatgpt tutorial",
            "trading stock market analysis",
        ]
        url = "https://www.googleapis.com/youtube/v3/search"

        for query in search_queries:
            try:
                params = {"part": "snippet", "q": query, "type": "video", "order": "relevance", "maxResults": 10, "key": api_key}
                resp = requests.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    for item in resp.json().get("items", []):
                        snippet = item.get("snippet", {})
                        videos.append({
                            "title": snippet.get("title", "Unknown"),
                            "channel": snippet.get("channelTitle", "Unknown"),
                            "views": "0",
                            "video_id": item.get("id", {}).get("videoId"),
                            "url": f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId')}",
                            "tags": snippet.get("tags", []),
                            "description": snippet.get("description", ""),
                        })
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Search failed for {query}: {e}")

        # Deduplicate
        seen = set()
        unique = [v for v in videos if v["video_id"] not in seen and not seen.add(v["video_id"])]
        videos = unique

        # Filter
        if ai_only:
            videos = [v for v in videos if is_ai_video(v.get("title", ""), v.get("tags"), v.get("description"))]
            logger.info(f"AI filter: {len(videos)} videos matched")

    else:
        # Use trending API
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {"part": "snippet,statistics", "chart": "mostPopular", "regionCode": "IN", "maxResults": 50, "key": api_key}

        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                for item in resp.json().get("items", []):
                    stats = item.get("statistics", {})
                    snippet = item.get("snippet", {})
                    videos.append({
                        "title": snippet.get("title", "Unknown"),
                        "channel": snippet.get("channelTitle", "Unknown"),
                        "views": stats.get("viewCount", "0"),
                        "video_id": item.get("id"),
                        "url": f"https://www.youtube.com/watch?v={item.get('id')}",
                    })
        except Exception as e:
            logger.error(f"API request failed: {e}")

    # Save
    clean = [{"title": v["title"], "channel": v["channel"], "views": v["views"], "video_id": v["video_id"], "url": v["url"]} for v in videos[:limit]]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2)

    logger.info(f"Scraped {len(clean)} videos")
    return clean


# ============================================================================
# SUMMARY FUNCTIONS
# ============================================================================

def generate_summary():
    """Generate AI summary using Claude."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    summary = "These videos cover the latest trends in AI and machine learning."

    if api_key:
        try:
            from anthropic import Anthropic
            # Load video data
            video_file = Path(".tmp/trending_raw.json")
            if not video_file.exists():
                return summary

            with open(video_file, "r", encoding="utf-8") as f:
                videos = json.load(f)

            titles = "\n".join([f"- {v['title']} ({v['channel']})" for v in videos[:5]])

            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": f"Summarize these YouTube videos in 2-3 sentences:\n{titles}"}]
            )
            summary = response.content[0].text
        except ImportError:
            logger.warning("Anthropic not installed - using basic summary")
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")

    # Save summary
    summary_file = Path(".tmp") / "ai_summary.txt"
    summary_file.write_text(summary, encoding="utf-8")
    logger.info(f"Summary: {summary[:100]}...")
    return summary


# ============================================================================
# FORMATTER FUNCTIONS
# ============================================================================

def format_views(views: str) -> str:
    """Format view count."""
    try:
        v = int(views)
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        elif v >= 1_000:
            return f"{v / 1_000:.1f}K"
        return str(v)
    except:
        return views


def format_report(limit: int = 5):
    """Format report for Telegram."""
    # Load data
    video_file = Path(".tmp/trending_raw.json")
    summary_file = Path(".tmp/ai_summary.txt")

    if not video_file.exists():
        logger.error("No video data found")
        return

    with open(video_file, "r", encoding="utf-8") as f:
        videos = json.load(f)

    summary = summary_file.read_text(encoding="utf-8") if summary_file.exists() else "Trending videos."

    # Format
    date = datetime.now().strftime("%d %b %Y")
    category = "Best Resources - AI Study & Data Analytics" if Path(".tmp/ai_mode.flag").exists() else "YouTube Trending India"

    message = f"""--- Message 1/1 ---
📚 <b>{category}</b>
🎯 Top Trending Videos
📅 {date}

💡 <b>Summary:</b>
{summary}
"""

    for i, v in enumerate(videos[:limit], 1):
        message += f"""
{i}. <b>{v['title']}</b>
   📺 {v['channel']} • 👁 {format_views(v['views'])}
   🔗 {v['url']}
"""

    message += "\n✨ <b>End of Report</b>"

    # Save
    report_file = Path(".tmp/trending_report.txt")
    report_file.write_text(message, encoding="utf-8")

    json_file = Path(".tmp/trending_formatted.json")
    json_file.write_text(json.dumps([{"text": message}], indent=2), encoding="utf-8")

    logger.info(f"Formatted {len(videos[:limit])} videos into 1 message(s)")


# ============================================================================
# NOTIFIER FUNCTIONS
# ============================================================================

def send_telegram():
    """Send message to Telegram."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.error("Missing Telegram credentials")
        return False

    # Load formatted message
    json_file = Path(".tmp/trending_formatted.json")
    if not json_file.exists():
        logger.error("No formatted message found")
        return False

    with open(json_file, "r", encoding="utf-8") as f:
        messages = json.load(f)

    # Send
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    for msg in messages:
        try:
            resp = requests.post(url, json={"chat_id": chat_id, "text": msg["text"], "parse_mode": "HTML"}, timeout=30)
            if resp.status_code == 200:
                logger.info(f"Sent successfully to {chat_id}")
            else:
                logger.error(f"Failed: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False

    return True


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="YouTube AI Digest")
    parser.add_argument("-n", "--limit", type=int, default=5, help="Number of videos")
    parser.add_argument("--ai", action="store_true", help="Filter for AI/ML content")
    parser.add_argument("--test", action="store_true", help="Use test data")
    parser.add_argument("--force", action="store_true", help="Skip duplicate check")
    args = parser.parse_args()

    logger.info(f"YouTube AI Digest - Starting at {datetime.now().isoformat()}")
    logger.info(f"Limit: {args.limit}, AI Mode: {args.ai}, Test: {args.test}")

    # Create AI mode flag
    if args.ai:
        Path(".tmp/ai_mode.flag").touch()

    # Step 1: Scrape
    logger.info("Step 1: Scraping YouTube...")
    videos = scrape_youtube(args.limit, test_mode=args.test, ai_only=args.ai)
    if not videos:
        logger.error("No videos scraped - exiting")
        return

    # Step 2: Summary
    logger.info("Step 2: Generating summary...")
    generate_summary()

    # Step 3: Format
    logger.info("Step 3: Formatting report...")
    format_report(args.limit)

    # Step 4: Send
    logger.info("Step 4: Sending to Telegram...")
    if send_telegram():
        logger.info("Message sent successfully!")
    else:
        logger.error("Failed to send message")

    logger.info(f"YouTube AI Digest - Completed at {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()