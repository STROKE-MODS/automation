#!/usr/bin/env python3
"""
Telegram Message Sender
Sends formatted messages to Telegram via Bot API.
"""

import json
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

load_dotenv()


# Telegram API configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(text: str) -> dict:
    """
    Send a text message via Telegram.

    Args:
        text: Message text to send

    Returns:
        Response dictionary
    """
    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()

        if data.get("ok"):
            return {"success": True, "message_id": data.get("result", {}).get("message_id")}
        return {"success": False, "error": data.get("description")}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def send_messages(messages: list[str]) -> dict:
    """
    Send multiple messages sequentially.

    Args:
        messages: List of message texts

    Returns:
        Summary of send results
    """
    results = []
    for i, msg in enumerate(messages, 1):
        print(f"Sending message {i}/{len(messages)}...")
        result = send_message(msg)
        results.append(result)

        if not result.get("success"):
            print(f"Failed: {result.get('error')}")
        else:
            print(f"Sent successfully")

    success_count = sum(1 for r in results if r.get("success"))
    return {
        "total": len(messages),
        "sent": success_count,
        "failed": len(messages) - success_count,
        "details": results
    }


def load_report_messages() -> list[str]:
    """Load formatted messages from the report file."""
    json_file = Path(".tmp") / "trending_formatted.json"

    if not json_file.exists():
        print(f"Error: No report found. Run format_trending_report.py first.", file=sys.stderr)
        return []

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)
        return data.get("messages", [])


def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env", file=sys.stderr)
        sys.exit(1)

    # Check bot info
    print(f"Configured for Chat ID: {TELEGRAM_CHAT_ID}")

    # Load and send messages
    messages = load_report_messages()
    if not messages:
        print("No messages to send", file=sys.stderr)
        sys.exit(1)

    print(f"\nSending {len(messages)} message(s) to Telegram...")
    result = send_messages(messages)

    print(f"\nResults: {result['sent']}/{result['total']} sent successfully")

    # Record analytics
    try:
        video_count = 0
        json_file = Path(".tmp") / "trending_raw.json"
        if json_file.exists():
            with open(json_file, encoding="utf-8") as f:
                video_count = len(json.load(f))

        # Run analytics tracker
        import subprocess
        subprocess.run([
            sys.executable, "scripts/telegram_analytics.py", "--report",
            str(len(messages)), str(video_count)
        ], check=False)
    except Exception as e:
        print(f"Analytics recording skipped: {e}")

    # Save result
    result_file = Path(".tmp") / "send_result.json"
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2)

    if result["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()