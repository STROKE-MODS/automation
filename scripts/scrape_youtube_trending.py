#!/usr/bin/env python3
"""
YouTube Trending Scraper
Fetches trending videos from YouTube India and outputs as JSON.
Supports filtering for AI/ML and Data Analytics topics.
"""

import json
import sys
import io
import re
import time
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.tmp/scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Fix Unicode output on Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

load_dotenv()

# Strong AI/ML keywords — any single match is enough
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
    "stable diffusion", "midjourney", "dall-e", "dalle", "diffusion model",
    "feature engineering", "model training", "hyperparameter",
    "gradient descent", "backpropagation", "convolutional",
    "recurrent neural", "lstm", "bert", "gpt4", "gpt-4", "gpt5", "gpt-5",
    "power bi", "tableau", "data visualization", "data pipeline",
    "etl", "big data", "hadoop", "spark", "sql", "nosql",
    "jupyter", "kaggle", "colab", "google colab",
    "trading", "stock market", "forex", "crypto", "binance", "coinbase",
    "options trading", "intraday", "nifty", "sensex", "zerodha", "upstox",
    "algorithmic trading", "price action", "technical analysis",
    "python programming", "learn python", "python tutorial",
    "data scientist", "ai engineer", "ml engineer",
    "artificial", "neurIPS", "icml",
]

# Channel names that are likely tech/education focused
AI_RELEVANT_CHANNELS = [
    "mkbhd", "marques brownlee", "two minute papers", "lex fridman",
    "sentdex", "python programmer", "corey schafer", "freecodecamp",
    "kaggle", "data school", " Krish Naik", "Abhishek Thakur",
    "code with harry", "chacha bro", "apna college", "pw skills",
    "great learning", "simplilearn", "edureka", "coursera", "udemy",
    "statquest", "3blue1brown", "numberphile",
]

# YouTube category IDs that boost relevance
AI_RELEVANT_CATEGORIES = {"27", "28"}  # 27=Education, 28=Science & Technology


def _keyword_match(text: str, keywords: list[str]) -> list[str]:
    """Return all keywords that match in text using word boundaries."""
    if not text:
        return []
    text_lower = text.lower()
    matched = []
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            matched.append(keyword)
    return matched


def is_ai_data_video(title: str, tags: list[str] = None,
                     description: str = None, category_id: str = None,
                     channel: str = None) -> bool:
    """
    Check if a video is AI/ML/Data Analytics/Trading content.

    Args:
        title: Video title
        tags: Video tags from YouTube API
        description: Video description (first 300 chars checked)
        category_id: YouTube category ID
        channel: Channel name
    """
    # Combine searchable text fields
    tags_text = " ".join(tags) if tags else ""
    desc_text = (description or "")[:300]
    channel_lower = channel.lower() if channel else ""

    all_text = f"{title} {tags_text} {desc_text}"

    # Check strong keywords - any single match is enough
    strong_hits = _keyword_match(all_text, AI_STRONG_KEYWORDS)
    if strong_hits:
        return True

    # Also check if channel is a known tech/education channel
    channel_hits = _keyword_match(channel_lower, AI_RELEVANT_CHANNELS)
    if channel_hits:
        return True

    return False


def scrape_youtube_trending(limit: int = 5, region: str = "IN,US", test_mode: bool = False, ai_only: bool = False) -> list[dict]:
    """
    Scrape YouTube trending videos using YouTube Data API.

    Args:
        limit: Number of videos to fetch (default 5)
        region: Country codes comma-separated (default: IN,US for India and US)
        test_mode: If True, return sample data for testing
        ai_only: If True, filter for AI/Data analytics videos only
    """
    output_file = Path(".tmp") / "trending_raw.json"
    output_file.parent.mkdir(exist_ok=True)

    videos = []
    regions = [r.strip() for r in region.split(",")]

    # Test mode with AI/Data analytics samples
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
                {"title": "Comedy Special - Full Episode", "channel": "Sony LIV", "views": "5000000", "video_id": "sample4", "url": "https://youtube.com/watch?v=sample4"},
                {"title": "Tech Review: Latest Smartphone", "channel": "Technical Guruji", "views": "3000000", "video_id": "sample5", "url": "https://youtube.com/watch?v=sample5"},
            ][:limit]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        print(f"Scraped {len(videos)} trending videos")
        return videos

    # Use YouTube Data API
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.warning("No YouTube API key found in .env - using test mode")
    else:
        # When AI mode, use search API instead of trending
        if ai_only:
            search_queries = [
                "AI machine learning tutorial",
                "data science tutorial",
                "python programming tutorial",
                "chatgpt tutorial",
                "artificial intelligence explained",
                "trading stock market analysis",
            ]
            url = "https://www.googleapis.com/youtube/v3/search"
            max_retries = 3

            for query in search_queries:
                for attempt in range(max_retries):
                    try:
                        params = {
                            "part": "snippet",
                            "q": query,
                            "type": "video",
                            "order": "relevance",
                            "maxResults": 10,
                            "key": api_key
                        }
                        logger.info(f"Searching YouTube for: {query}")
                        resp = requests.get(url, params=params, timeout=15)
                        if resp.status_code == 200:
                            data = resp.json()
                            if "error" in data:
                                logger.error(f"YouTube API error: {data['error'].get('message', 'Unknown error')}")
                                break
                            for item in data.get("items", []):
                                snippet = item.get("snippet", {})
                                title = snippet.get("title", "Unknown")
                                videos.append({
                                    "title": title,
                                    "channel": snippet.get("channelTitle", "Unknown"),
                                    "views": "0",  # Search API doesn't return views
                                    "video_id": item.get("id", {}).get("videoId"),
                                    "url": f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId')}",
                                    "tags": snippet.get("tags", []),
                                    "description": snippet.get("description", ""),
                                    "category_id": "",
                                })
                            break
                        elif resp.status_code == 403:
                            logger.error(f"YouTube API rate limit exceeded (403 Forbidden)")
                            break
                        else:
                            logger.warning(f"YouTube API returned status {resp.status_code}")
                    except Exception as e:
                        logger.warning(f"Search failed: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                # Small delay between queries
                time.sleep(1)

            logger.info(f"Total videos from search: {len(videos)}")
        else:
            # Original trending approach
            url = "https://www.googleapis.com/youtube/v3/videos"
            max_retries = 3
            retry_delay = 2

            for r in regions:
                for attempt in range(max_retries):
                    try:
                        params = {
                            "part": "snippet,statistics",
                            "chart": "mostPopular",
                            "regionCode": r,
                            "maxResults": 50,
                            "key": api_key
                        }
                        logger.info(f"Fetching YouTube trending for {r} (attempt {attempt + 1}/{max_retries})")
                        resp = requests.get(url, params=params, timeout=15)
                        if resp.status_code == 200:
                            data = resp.json()
                            if "error" in data:
                                logger.error(f"YouTube API error: {data['error'].get('message', 'Unknown error')}")
                                break
                            for item in data.get("items", []):
                                stats = item.get("statistics", {})
                                snippet = item.get("snippet", {})
                                title = snippet.get("title", "Unknown")
                                videos.append({
                                    "title": title,
                                    "channel": snippet.get("channelTitle", "Unknown"),
                                    "views": stats.get("viewCount", "0"),
                                    "video_id": item.get("id"),
                                    "url": f"https://www.youtube.com/watch?v={item.get('id')}",
                                    "tags": snippet.get("tags", []),
                                    "description": snippet.get("description", ""),
                                    "category_id": snippet.get("categoryId", ""),
                                })
                            logger.info(f"Fetched {len([v for v in videos if v.get('region') == r])} videos from {r}")
                            break
                        elif resp.status_code == 403:
                            logger.error(f"YouTube API rate limit exceeded (403 Forbidden)")
                            break
                        elif resp.status_code == 400:
                            logger.error(f"YouTube API bad request (400): {resp.text}")
                            break
                        else:
                            logger.warning(f"YouTube API returned status {resp.status_code}")
                    except requests.exceptions.RequestException as e:
                        logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"All {max_retries} attempts failed")
                    except Exception as e:
                        logger.error(f"Unexpected error during API call: {e}")
                        break

        # Deduplicate by video_id
        seen = set()
        unique_videos = []
        for v in videos:
            if v["video_id"] and v["video_id"] not in seen:
                seen.add(v["video_id"])
                unique_videos.append(v)
        videos = unique_videos
        logger.info(f"Total unique videos after dedup: {len(videos)}")

    # Filter for AI/Data analytics if requested
    if ai_only:
        filtered = [v for v in videos if is_ai_data_video(
            title=v.get("title", ""),
            tags=v.get("tags"),
            description=v.get("description"),
            category_id=v.get("category_id"),
            channel=v.get("channel"),
        )]
        logger.info(f"AI filter: {len(filtered)}/{len(videos)} videos matched")
        videos = filtered[:limit]
        # Create flag file for format_trending_report.py
        Path(".tmp").mkdir(exist_ok=True)
        Path(".tmp", "ai_mode.flag").touch()
    else:
        # Remove flag if not in AI mode
        flag_file = Path(".tmp", "ai_mode.flag")
        if flag_file.exists():
            flag_file.unlink()

    # Strip internal metadata before saving (tags/description/category_id are only for filtering)
    clean_videos = []
    for v in videos:
        clean_videos.append({
            "title": v.get("title", "Unknown"),
            "channel": v.get("channel", "Unknown"),
            "views": v.get("views", "0"),
            "video_id": v.get("video_id"),
            "url": v.get("url", ""),
        })

    # Save raw data
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clean_videos, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(clean_videos)} trending videos")
    return clean_videos


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    test_mode = "--test" in sys.argv or "-t" in sys.argv
    ai_only = "--ai" in sys.argv or "-a" in sys.argv
    scrape_youtube_trending(limit, test_mode=test_mode, ai_only=ai_only)