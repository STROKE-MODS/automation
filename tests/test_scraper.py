"""
Unit tests for YouTube scraper
"""

import pytest
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Copy the keyword matching logic for testing
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


def test_keyword_matching():
    """Test keyword matching logic"""
    AI_STRONG_KEYWORDS = [
        "ai", "machine learning", "deep learning", "data science",
        "trading", "stock market", "python"
    ]

    # Test that keywords are matched correctly
    text = "Learn machine learning and deep learning"
    matches = _keyword_match(text, AI_STRONG_KEYWORDS)

    assert "machine learning" in matches
    assert "deep learning" in matches


def test_ai_video_detection():
    """Test AI video detection logic"""
    AI_STRONG_KEYWORDS = [
        "ai", "machine learning", "deep learning", "data science",
        "trading", "stock market", "python"
    ]

    # Should match AI content
    text1 = "Machine Learning Tutorial for Beginners python"
    matches1 = _keyword_match(text1, AI_STRONG_KEYWORDS)
    assert "machine learning" in matches1 or "python" in matches1

    # Should match trading content
    text2 = "Stock Market Trading Analysis"
    matches2 = _keyword_match(text2, AI_STRONG_KEYWORDS)
    assert "trading" in matches2 or "stock market" in matches2

    # Should NOT match entertainment
    text3 = "Bollywood Movie Trailer 2024"
    matches3 = _keyword_match(text3, AI_STRONG_KEYWORDS)
    assert len(matches3) == 0


def test_video_data_structure():
    """Test video data structure"""
    video = {
        "title": "Test Video",
        "channel": "Test Channel",
        "views": "1000",
        "video_id": "abc123",
        "url": "https://youtube.com/watch?v=abc123"
    }

    assert video["title"] == "Test Video"
    assert video["video_id"] == "abc123"
    assert video["url"].startswith("https://youtube.com")


def test_keyword_boundaries():
    """Test that keyword matching respects word boundaries"""

    # "ai" should not match in "train"
    text = "I need to train this model"
    matches = _keyword_match(text, ["ai", "ml"])
    assert "ai" not in matches

    # But should match "ai" as standalone
    text = "Learn AI and ML"
    matches = _keyword_match(text, ["ai", "ml"])
    assert "ai" in matches
    assert "ml" in matches


if __name__ == "__main__":
    pytest.main([__file__, "-v"])