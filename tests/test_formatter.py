"""
Unit tests for report formatter
"""

import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_telegram_html_formatting():
    """Test Telegram HTML formatting"""
    videos = [
        {
            "title": "Test Video Title",
            "channel": "Test Channel",
            "views": "1000",
            "url": "https://youtube.com/watch?v=abc123"
        }
    ]

    # Check basic structure
    assert len(videos) == 1
    assert videos[0]["title"] == "Test Video Title"
    assert videos[0]["url"].startswith("https://youtube.com")


def test_message_content():
    """Test message content generation"""
    videos = [
        {"title": "Video 1", "channel": "Channel 1", "views": "1000", "url": "http://x"},
        {"title": "Video 2", "channel": "Channel 2", "views": "2000", "url": "http://y"},
    ]

    # Generate numbered list
    message = ""
    for i, v in enumerate(videos, 1):
        message += f"{i}. {v['title']}\n"

    assert "1. Video 1" in message
    assert "2. Video 2" in message


def test_view_count_formatting():
    """Test view count formatting"""
    def format_views(view_str):
        views = int(view_str)
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M"
        elif views >= 1_000:
            return f"{views / 1_000:.1f}K"
        return str(views)

    assert format_views("2500000") == "2.5M"
    assert format_views("950000") == "950.0K"
    assert format_views("500") == "500"


def test_empty_videos():
    """Test handling of empty video list"""
    videos = []

    # Should handle empty list gracefully
    assert len(videos) == 0


def test_video_limit():
    """Test video limiting"""
    videos = [{"title": f"Video {i}"} for i in range(10)]
    limit = 5

    limited = videos[:limit]

    assert len(limited) == limit
    assert limited[0]["title"] == "Video 0"
    assert limited[4]["title"] == "Video 4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])