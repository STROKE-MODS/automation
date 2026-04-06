#!/usr/bin/env python3
"""
YouTube Weekly Report Orchestrator
Runs the complete workflow: scrape -> generate summary -> format -> send
"""

import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import json

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


def run_tool(script_path: str, args: list[str] = None, required: bool = True) -> bool:
    """
    Run a Python tool script and handle errors.

    Args:
        script_path: Path to the Python script
        args: Command-line arguments
        required: If True, failure stops the workflow

    Returns:
        True if successful, False otherwise
    """
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)

    logger.info(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            logger.info(f"Success: {script_path}")
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        logger.info(f"  {line}")
            return True
        else:
            logger.error(f"Failed: {script_path} (exit code {result.returncode})")
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    logger.error(f"  {line}")
            if required:
                return False
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout: {script_path} took too long")
        if required:
            return False
    except Exception as e:
        logger.error(f"Error running {script_path}: {e}")
        if required:
            return False
    return False


def check_previous_sent(limit: int = 5, ai_only: bool = False) -> bool:
    """Check if the same report was already sent recently."""
    from datetime import datetime, timedelta

    sent_history_file = Path(".tmp/sent_history.json")
    if not sent_history_file.exists():
        return False

    try:
        with open(sent_history_file, "r") as f:
            history = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return False

    # Check if sent in the last 6 hours
    six_hours_ago = datetime.now() - timedelta(hours=6)
    for entry in history:
        try:
            sent_time = datetime.fromisoformat(entry.get("timestamp", ""))
            if sent_time > six_hours_ago:
                if entry.get("limit") == limit and entry.get("ai_only") == ai_only:
                    logger.warning(f"Similar report already sent at {entry.get('timestamp')}")
                    return True
        except (ValueError, TypeError):
            continue

    return False


def mark_as_sent(limit: int = 5, ai_only: bool = False):
    """Mark this report as sent to prevent duplicates."""
    sent_history_file = Path(".tmp/sent_history.json")

    history = []
    if sent_history_file.exists():
        try:
            with open(sent_history_file, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []

    # Add new entry
    history.append({
        "timestamp": datetime.now().isoformat(),
        "limit": limit,
        "ai_only": ai_only
    })

    # Keep only last 50 entries
    history = history[-50:]

    with open(sent_history_file, "w") as f:
        json.dump(history, f, indent=2)


def main():
    """Main orchestrator workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Weekly Report Orchestrator")
    parser.add_argument("-n", "--limit", type=int, default=5, help="Number of videos to fetch")
    parser.add_argument("--ai", action="store_true", help="Filter for AI/Data analytics only")
    parser.add_argument("--test", action="store_true", help="Use test mode (no real API calls)")
    parser.add_argument("--force", action="store_true", help="Force send even if recently sent")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip scraping (use existing data)")
    parser.add_argument("--skip-summary", action="store_true", help="Skip AI summary generation")
    parser.add_argument("--skip-format", action="store_true", help="Skip formatting")
    parser.add_argument("--skip-send", action="store_true", help="Skip sending message")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info(f"YouTube Weekly Report - Starting at {datetime.now().isoformat()}")
    logger.info(f"Limit: {args.limit}, AI Mode: {args.ai}, Test: {args.test}")
    logger.info("=" * 60)

    # Check for duplicates (unless force is used)
    if not args.force:
        if check_previous_sent(args.limit, args.ai):
            logger.warning("Duplicate check: similar report sent recently. Use --force to override.")
            logger.info("Use --force to override and send anyway.")
            return

    # Step 1: Scrape YouTube Trending
    if not args.skip_scrape:
        tool_args = [str(args.limit)]
        if args.test:
            tool_args.append("--test")
        if args.ai:
            tool_args.append("--ai")

        if not run_tool("tools/scrape_youtube_trending.py", tool_args, required=True):
            logger.error("Step 1 failed: Scrape YouTube Trending")
            logger.error("Workflow aborted")
            return
    else:
        logger.info("Skipping scrape (using existing data)")

    # Step 2: Generate AI Summary
    if not args.skip_summary:
        if not run_tool("tools/generate_video_summary.py", required=True):
            logger.warning("Step 2 failed: Generate AI Summary (continuing anyway)")
    else:
        logger.info("Skipping AI summary generation")

    # Step 3: Format Report
    if not args.skip_format:
        if not run_tool("tools/format_trending_report.py", [str(args.limit)], required=True):
            logger.error("Step 3 failed: Format Report")
            logger.error("Workflow aborted")
            return
    else:
        logger.info("Skipping formatting")

    # Step 4: Send via Telegram
    if not args.skip_send:
        if not run_tool("tools/send_telegram_message.py", required=True):
            logger.error("Step 4 failed: Send Telegram Message")
            logger.error("Workflow aborted")
            return
        # Mark as sent only if successfully sent
        mark_as_sent(args.limit, args.ai)
    else:
        logger.info("Skipping Telegram send")

    logger.info("=" * 60)
    logger.info(f"YouTube Weekly Report - Completed at {datetime.now().isoformat()}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()