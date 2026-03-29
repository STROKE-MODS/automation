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
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

# Fix Unicode output on Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

load_dotenv()

# Keywords for AI/ML and Data Analytics filtering
AI_DATA_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "data science", "data analytics", "data analysis", "python", "tensorflow",
    "pytorch", "keras", "pandas", "numpy", "statistics", "analytics",
    "chatgpt", "gpt", "llm", "large language model", "neural network",
    "algorithm", "coding", "programming", "tutorial", "course", "learn",
    "data engineer", "data scientist", "mlops", "autogpt", "copilot"
]


def is_ai_data_video(title: str) -> bool:
    """Check if video title contains AI/Data analytics keywords."""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in AI_DATA_KEYWORDS)


def scrape_youtube_trending(limit: int = 5, region: str = "IN", test_mode: bool = False, ai_only: bool = False) -> list[dict]:
    """
    Scrape YouTube trending videos using YouTube Data API.

    Args:
        limit: Number of videos to fetch (default 5)
        region: Country code (default: IN for India)
        test_mode: If True, return sample data for testing
        ai_only: If True, filter for AI/Data analytics videos only
    """
    output_file = Path(".tmp") / "trending_raw.json"
    output_file.parent.mkdir(exist_ok=True)

    videos = []

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
    if api_key:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": 50,  # Fetch more to filter
            "key": api_key
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    stats = item.get("statistics", {})
                    snippet = item.get("snippet", {})
                    title = snippet.get("title", "Unknown")
                    videos.append({
                        "title": title,
                        "channel": snippet.get("channelTitle", "Unknown"),
                        "views": stats.get("viewCount", "0"),
                        "video_id": item.get("id"),
                        "url": f"https://www.youtube.com/watch?v={item.get('id')}"
                    })
        except requests.exceptions.RequestException:
            pass

    # Filter for AI/Data analytics if requested
    if ai_only:
        filtered = [v for v in videos if is_ai_data_video(v.get("title", ""))]
        videos = filtered[:limit]
        # Create flag file for format_trending_report.py
        Path(".tmp").mkdir(exist_ok=True)
        Path(".tmp", "ai_mode.flag").touch()

    # Save raw data
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(videos)} trending videos")
    return videos


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    test_mode = "--test" in sys.argv or "-t" in sys.argv
    ai_only = "--ai" in sys.argv or "-a" in sys.argv
    scrape_youtube_trending(limit, test_mode=test_mode, ai_only=ai_only)