#!/usr/bin/env python3
"""
Telegram Analytics Tracker
Tracks user interactions, message sends, and usage analytics.
Records Telegram username, date/time, and usage statistics.
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Fix Unicode output on Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

ANALYTICS_FILE = Path(".tmp") / "analytics.json"


def load_analytics() -> dict:
    """Load existing analytics data."""
    if ANALYTICS_FILE.exists():
        with open(ANALYTICS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "total_reports_sent": 0,
        "total_messages_sent": 0,
        "first_use": None,
        "last_use": None,
        "users": {},
        "daily_stats": {}
    }


def save_analytics(data: dict) -> None:
    """Save analytics data to file."""
    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_chat_info(chat_id: str) -> dict:
    """Get chat information from Telegram to retrieve user details."""
    try:
        url = f"{BASE_URL}/getChat"
        resp = requests.get(url, params={"chat_id": chat_id}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("result", {})
    except requests.exceptions.RequestException:
        pass
    return {}


def get_user_info(chat_id: str) -> dict:
    """Get user information from Telegram."""
    try:
        url = f"{BASE_URL}/getChatMember"
        # Try to get the bot's own info first, then chat admins
        for user_id in ["me", "all"]:
            resp = requests.get(url, params={"chat_id": chat_id, "user_id": user_id}, timeout=10)
            if resp.status_code == 200:
                result = resp.json().get("result", {})
                if result.get("user"):
                    return result["user"]
    except requests.exceptions.RequestException:
        pass
    return {}


def record_report_sent(chat_id: str, message_count: int, video_count: int = 0) -> dict:
    """
    Record a report being sent to a user.
    Updates analytics with timestamp, username, and usage stats.
    """
    data = load_analytics()

    # Get current timestamp
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    datetime_str = now.isoformat()

    # Get user info
    chat_info = get_chat_info(str(chat_id))
    username = chat_info.get("username", chat_info.get("first_name", "Unknown"))
    first_name = chat_info.get("first_name", "")
    last_name = chat_info.get("last_name", "")

    # Build user identifier
    user_key = str(chat_id)
    full_name = f"{first_name} {last_name}".strip() if first_name else username

    # Update overall stats
    data["total_reports_sent"] = data.get("total_reports_sent", 0) + 1
    data["total_messages_sent"] = data.get("total_messages_sent", 0) + message_count

    if not data.get("first_use"):
        data["first_use"] = datetime_str
    data["last_use"] = datetime_str

    # Update user-specific stats
    if user_key not in data["users"]:
        data["users"][user_key] = {
            "username": username,
            "full_name": full_name,
            "first_interaction": datetime_str,
            "reports_received": 0,
            "messages_received": 0
        }

    data["users"][user_key]["reports_received"] += 1
    data["users"][user_key]["messages_received"] += message_count
    data["users"][user_key]["last_interaction"] = datetime_str

    # Update daily stats
    if date_str not in data["daily_stats"]:
        data["daily_stats"][date_str] = {
            "reports_sent": 0,
            "messages_sent": 0,
            "unique_users": []
        }

    # Ensure unique_users is a list
    if isinstance(data["daily_stats"][date_str]["unique_users"], list):
        if user_key not in data["daily_stats"][date_str]["unique_users"]:
            data["daily_stats"][date_str]["unique_users"].append(user_key)
    else:
        # Convert set to list if it exists as set
        data["daily_stats"][date_str]["unique_users"] = list(data["daily_stats"][date_str].get("unique_users", []))
        if user_key not in data["daily_stats"][date_str]["unique_users"]:
            data["daily_stats"][date_str]["unique_users"].append(user_key)

    data["daily_stats"][date_str]["reports_sent"] += 1
    data["daily_stats"][date_str]["messages_sent"] += message_count

    # Ensure unique_user_count exists
    data["daily_stats"][date_str]["unique_user_count"] = len(data["daily_stats"][date_str]["unique_users"])

    save_analytics(data)

    return {
        "recorded": True,
        "user": username,
        "full_name": full_name,
        "chat_id": chat_id,
        "datetime": datetime_str,
        "date": date_str,
        "time": time_str,
        "messages_sent": message_count,
        "videos_in_report": video_count
    }


def get_analytics_summary() -> dict:
    """Get a summary of analytics."""
    data = load_analytics()

    # Calculate unique users count
    unique_users = len(data.get("users", {}))

    # Get last 7 days stats
    now = datetime.now()
    last_7_days = {}
    for i in range(7):
        d = now.replace(hour=0, minute=0, second=0, microsecond=0)
        d = d.replace(day=now.day - i)
        date_key = d.strftime("%Y-%m-%d")
        if date_key in data.get("daily_stats", {}):
            last_7_days[date_key] = data["daily_stats"][date_key]

    return {
        "total_reports_sent": data.get("total_reports_sent", 0),
        "total_messages_sent": data.get("total_messages_sent", 0),
        "unique_users": unique_users,
        "first_use": data.get("first_use"),
        "last_use": data.get("last_use"),
        "last_7_days": last_7_days,
        "users": data.get("users", {})
    }


def format_analytics_report() -> str:
    """Format analytics as a human-readable report."""
    summary = get_analytics_summary()

    lines = [
        "📊 *Analytics Report*",
        "",
        f"📈 *Total Reports:* {summary['total_reports_sent']}",
        f"💬 *Total Messages:* {summary['total_messages_sent']}",
        f"👥 *Unique Users:* {summary['unique_users']}",
        "",
        "*Last Usage:*"
    ]

    if summary.get("last_use"):
        last = datetime.fromisoformat(summary["last_use"])
        lines.append(f"  • Last: {last.strftime('%d %b %Y %H:%M')}")

    if summary.get("first_use"):
        first = datetime.fromisoformat(summary["first_use"])
        lines.append(f"  • First: {first.strftime('%d %b %Y %H:%M')}")

    if summary.get("users"):
        lines.append("")
        lines.append("*User Activity:*")
        for user_id, user_data in summary["users"].items():
            lines.append(f"  • {user_data.get('username', 'Unknown')}: {user_data.get('reports_received', 0)} reports")

    return "\n".join(lines)


def main():
    # Check if recording a new report
    if "--report" in sys.argv:
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")
        message_count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        video_count = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        result = record_report_sent(chat_id, message_count, video_count)
        print(f"Recorded: {result['user']} at {result['datetime']}")
        return

    # Check if showing summary
    if "--summary" in sys.argv:
        print(format_analytics_report())
        return

    # Default: show full analytics
    summary = get_analytics_summary()
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()