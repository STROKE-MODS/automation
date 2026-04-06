#!/usr/bin/env python3
"""
Trending Report Formatter
Converts YouTube trending JSON to crisp WhatsApp-friendly text format.
"""

import json
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix Unicode output on Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass


def format_views(views_str: str) -> str:
    """Convert view count to human-readable format."""
    try:
        views = int(views_str)
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M"
        elif views >= 1_000:
            return f"{views / 1_000:.1f}K"
        return str(views)
    except (ValueError, TypeError):
        return views_str if views_str else "N/A"


def load_ai_summary() -> str:
    """Load AI-generated summary if available."""
    summary_file = Path(".tmp") / "ai_summary.txt"
    if summary_file.exists():
        with open(summary_file, encoding="utf-8") as f:
            return f.read().strip()
    return ""


def check_ai_mode() -> bool:
    """Check if running in AI/Data analytics mode."""
    return (Path(".tmp") / "ai_mode.flag").exists()


def format_trending_report(videos: list[dict], max_videos: int = 20) -> list[str]:
    """
    Format trending videos into crisp WhatsApp messages.

    Args:
        videos: List of video dictionaries
        max_videos: Maximum videos to include

    Returns:
        List of message chunks (WhatsApp-friendly)
    """
    if not videos:
        return ["No trending videos found."]

    # Header with AI summary
    date_str = datetime.now().strftime("%d %b %Y")
    ai_summary = load_ai_summary()
    is_ai_mode = check_ai_mode()

    # Custom header based on mode (using HTML for Telegram)
    if is_ai_mode:
        header = f"📚 <b>Best Resources - AI Study & Data Analytics</b>\n🎯 Top Trending Videos\n📅 {date_str}\n"
    else:
        header = f"📊 <b>YouTube Trending India</b>\n📅 Week of {date_str}\n"

    if ai_summary:
        header += f"\n💡 <b>Summary:</b>\n{ai_summary}\n"

    messages = []
    current_msg = header

    for i, video in enumerate(videos[:max_videos], 1):
        title = video.get("title", "Unknown")[:60]  # Truncate long titles
        if len(title) >= 60:
            title += "..."

        channel = video.get("channel", "Unknown")
        views = format_views(video.get("views", "0"))
        url = video.get("url", "")

        # Format each video entry
        entry = (
            f"\n{i}. <b>{title}</b>\n"
            f"   📺 {channel} • 👁 {views}\n"
            f"   🔗 {url}"
        )

        # Check if adding this would exceed WhatsApp limit (~4096 chars)
        if len(current_msg) + len(entry) > 3500:
            messages.append(current_msg)
            current_msg = header + entry
        else:
            current_msg += entry

    # Footer
    current_msg += "\n\n✨ <b>End of Report</b>"
    messages.append(current_msg)

    return messages


def main():
    input_file = Path(".tmp") / "trending_raw.json"

    if not input_file.exists():
        print(f"Error: {input_file} not found. Run scrape_youtube_trending.py first.", file=sys.stderr)
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        videos = json.load(f)

    max_videos = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    messages = format_trending_report(videos, max_videos)

    # Force to single message if multiple (truncate to fit)
    if len(messages) > 1:
        combined = "\n".join(messages)
        # Telegram max message is 4096 chars
        if len(combined) > 4000:
            combined = combined[:3990] + "\n\n... (truncated)"
        messages = [combined]

    # Save formatted messages
    output_file = Path(".tmp") / "trending_report.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for i, msg in enumerate(messages, 1):
            f.write(f"--- Message {i}/{len(messages)} ---\n")
            f.write(msg)
            f.write("\n\n")

    print(f"Formatted {len(videos)} videos into {len(messages)} message(s)")
    print(f"Saved to: {output_file}")

    # Save JSON for programmatic use
    json_output = {
        "message_count": len(messages),
        "video_count": len(videos),
        "messages": messages
    }
    json_file = Path(".tmp") / "trending_formatted.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"JSON saved to: {json_file}")


if __name__ == "__main__":
    main()