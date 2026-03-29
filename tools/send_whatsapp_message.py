#!/usr/bin/env python3
"""
WhatsApp Message Sender via Wppconnect
Sends formatted messages to a phone number via local Wppconnect server.
"""

import json
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

load_dotenv()


# Wppconnect server configuration
WPP_HOST = os.getenv("WPP_HOST", "http://localhost")
WPP_PORT = os.getenv("WPP_PORT", "21465")
WPP_TOKEN = os.getenv("WPP_TOKEN", "")  # Optional session token

BASE_URL = f"{WPP_HOST}:{WPP_PORT}/api"


def get_session_info() -> dict:
    """Check Wppconnect server status and get session info."""
    try:
        resp = requests.get(f"{BASE_URL}/status", timeout=10)
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def send_text_message(phone: str, message: str, session: str = "default") -> dict:
    """
    Send a text message via Wppconnect.

    Args:
        phone: Phone number with country code (e.g., "919999999999")
        message: Message text to send
        session: Wppconnect session name

    Returns:
        Response dictionary
    """
    url = f"{BASE_URL}/sendtext"

    payload = {
        "phone": phone,
        "message": message,
        "session": session
    }

    if WPP_TOKEN:
        payload["token"] = WPP_TOKEN

    try:
        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()

        if data.get("success"):
            return {"success": True, "message_id": data.get("id")}
        return {"success": False, "error": data.get("message")}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def send_messages(phone: str, messages: list[str]) -> dict:
    """
    Send multiple messages sequentially.

    Args:
        phone: Phone number with country code
        messages: List of message texts

    Returns:
        Summary of send results
    """
    results = []
    for i, msg in enumerate(messages, 1):
        print(f"Sending message {i}/{len(messages)}...")
        result = send_text_message(phone, msg)
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
    report_file = Path(".tmp") / "trending_report.txt"

    if not report_file.exists():
        # Try JSON format
        json_file = Path(".tmp") / "trending_formatted.json"
        if json_file.exists():
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
                return data.get("messages", [])

        print(f"Error: No report found. Run format_trending_report.py first.", file=sys.stderr)
        return []

    # Parse from text file
    with open(report_file, encoding="utf-8") as f:
        content = f.read()

    messages = []
    current_msg = ""
    in_message = False

    for line in content.split("\n"):
        if line.startswith("--- Message"):
            in_message = True
            current_msg = ""
        elif line.startswith("---") and in_message:
            if current_msg:
                messages.append(current_msg)
            in_message = False
        elif in_message:
            current_msg += line + "\n"

    if current_msg:
        messages.append(current_msg)

    return messages


def main():
    # Get phone number from args or environment
    phone = sys.argv[1] if len(sys.argv) > 1 else os.getenv("WHATSAPP_PHONE")

    if not phone:
        print("Usage: python send_whatsapp_message.py <phone_number>")
        print("   Or set WHATSAPP_PHONE in .env")
        print("   Phone format: 919999999999 (with country code, no +)")
        sys.exit(1)

    # Check server status
    print("Checking Wppconnect server...")
    status = get_session_info()
    print(f"Server status: {status}")

    if not status.get("success"):
        print(f"Warning: {status.get('error')}")
        print("Make sure Wppconnect server is running!")

    # Load and send messages
    messages = load_report_messages()
    if not messages:
        print("No messages to send", file=sys.stderr)
        sys.exit(1)

    print(f"\nSending {len(messages)} message(s) to {phone}...")
    result = send_messages(phone, messages)

    print(f"\nResults: {result['sent']}/{result['total']} sent successfully")

    # Save result
    result_file = Path(".tmp") / "send_result.json"
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2)

    if result["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()