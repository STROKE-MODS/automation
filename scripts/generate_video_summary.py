#!/usr/bin/env python3
"""
Video Summary Generator using Claude Code
Analyzes trending videos and generates crisp AI summaries.
"""

import json
import subprocess
import sys
import io
from pathlib import Path

# Fix Unicode output on Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass


def generate_summary(videos: list[dict]) -> str:
    """
    Use Claude Code CLI to analyze trending videos and generate summary.

    Args:
        videos: List of video dictionaries

    Returns:
        AI-generated summary text
    """
    # Prepare video data for analysis
    video_list = []
    for v in videos[:5]:
        video_list.append(f"- {v.get('title', 'Unknown')} ({v.get('channel', 'Unknown')})")

    videos_text = "\n".join(video_list)

    prompt = f"""Analyze these YouTube trending videos and give a 2-line summary:

{videos_text}

Reply with just 2 sentences max. No formatting."""

    # Call Claude Code CLI with longer timeout
    cmd = ["claude", "--print", "-p", prompt]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            input=""
        )

        if result.returncode != 0:
            return f"Summary: {videos[0].get('title', 'Trending videos')}" if videos else "No videos"

        summary = result.stdout.strip()
        if not summary:
            return f"Top video: {videos[0].get('title', 'Trending')}" if videos else "No videos"
        return summary

    except subprocess.TimeoutExpired:
        return f"Trending: {videos[0].get('title', 'Videos')}" if videos else "No videos"
    except Exception as e:
        return f"Trending now: {videos[0].get('title', 'Videos')}" if videos else "No videos"


def main():
    input_file = Path(".tmp") / "trending_raw.json"

    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        videos = json.load(f)

    print("Analyzing with Claude...")
    summary = generate_summary(videos)

    # Save summary
    output_file = Path(".tmp") / "ai_summary.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary: {summary[:50]}...")


if __name__ == "__main__":
    main()