#!/usr/bin/env python3
"""
Orchestration Script for YouTube Weekly Report
Runs the complete workflow with error handling, duplicate prevention, and logging.
"""

import sys
import json
import os
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

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

# Load environment
load_dotenv()


def verify_credentials():
    """Verify that required credentials are present."""
    required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        logger.error(f"Missing required credentials: {missing}")
        return False
    logger.info("Credentials verified successfully")
    return True


def get_video_hash(video):
    """Generate a unique hash for a video to detect duplicates."""
    content = f"{video.get('video_id', '')}{video.get('title', '')}"
    return hashlib.md5(content.encode()).hexdigest()


def load_sent_history():
    """Load the history of sent video hashes."""
    history_file = Path(".tmp") / "sent_history.json"
    if history_file.exists():
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sent_hashes": [], "last_sent": None}


def save_sent_history(history, new_hashes):
    """Save updated sent history."""
    history_file = Path(".tmp") / "sent_history.json"
    history["sent_hashes"].extend(new_hashes)
    history["last_sent"] = datetime.now().isoformat()
    history_file.parent.mkdir(exist_ok=True)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    logger.info(f"Updated sent history with {len(new_hashes)} new hashes")


def filter_new_videos(videos, history):
    """Filter out videos that have already been sent."""
    sent_hashes = set(history.get("sent_hashes", []))
    new_videos = []
    for video in videos:
        video_hash = get_video_hash(video)
        if video_hash not in sent_hashes:
            new_videos.append(video)
            video["hash"] = video_hash  # Add hash for tracking
        else:
            logger.info(f"Skipping already sent video: {video.get('title', 'Unknown')}")
    return new_videos


def run_step(command, step_name, continue_on_error=False):
    """Run a Python tool command and handle errors."""
    import subprocess
    logger.info(f"Running step: {step_name}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            logger.info(f"Step '{step_name}' completed successfully")
            if result.stdout:
                logger.debug(result.stdout)
            return True
        else:
            logger.error(f"Step '{step_name}' failed with code {result.returncode}")
            logger.error(result.stderr)
            if not continue_on_error:
                return False
    except subprocess.TimeoutExpired:
        logger.error(f"Step '{step_name}' timed out")
        if not continue_on_error:
            return False
    except Exception as e:
        logger.error(f"Error running '{step_name}': {e}")
        if not continue_on_error:
            return False
    return not continue_on_error or True


def run_workflow(ai_mode=True, limit=5, skip_ai_filter=False):
    """Run the complete YouTube weekly report workflow."""
    logger.info("=" * 50)
    logger.info("Starting YouTube Weekly Report Workflow")
    logger.info("=" * 50)

    # Validate inputs
    if limit < 1 or limit > 50:
        logger.error(f"Invalid limit: {limit}. Must be between 1 and 50.")
        return False

    # Step 1: Verify credentials
    if not verify_credentials():
        logger.error("Credential verification failed. Exiting.")
        return False

    # Step 2: Scrape YouTube trending
    cmd = f'python tools/scrape_youtube_trending.py {limit}'
    if ai_mode:
        cmd += ' --ai'
    # Use test mode if YOUTUBE_API_KEY is not set or for safety
    if not os.getenv("YOUTUBE_API_KEY"):
        cmd += ' --test'
        logger.info("No YouTube API key - using test mode")
    if not run_step(cmd, "Scrape YouTube Trending"):
        return False

    # Step 3: Generate AI summary
    if not run_step('python tools/generate_video_summary.py', "Generate AI Summary"):
        logger.warning("AI summary generation failed, continuing...")
    # Step 4: Format report
    if not run_step(f'python tools/format_trending_report.py {limit}', "Format Report"):
        return False

    # Step 5: Load and filter for new videos (duplicate prevention)
    history = load_sent_history()

    trending_file = Path(".tmp") / "trending_raw.json"
    if trending_file.exists():
        with open(trending_file, "r", encoding="utf-8") as f:
            videos = json.load(f)

        new_videos = filter_new_videos(videos, history)

        if not new_videos:
            logger.warning("No new videos to send. All videos have already been sent.")
            # Still send a message but indicate no new content
            new_videos = videos  # Fall back to all videos if none new
        else:
            logger.info(f"Found {len(new_videos)} new videos out of {len(videos)} total")

        # Save filtered videos for sending
        with open(trending_file, "w", encoding="utf-8") as f:
            json.dump(new_videos, f, indent=2, ensure_ascii=False)
    else:
        logger.error("No trending data found")
        return False

    # Step 6: Send via Telegram
    if not run_step('python tools/send_telegram_message.py', "Send Telegram Message"):
        return False

    # Step 7: Update sent history with only new unique hashes
    new_hashes = []
    for v in new_videos:
        h = v.get("hash", get_video_hash(v))
        if h not in history.get("sent_hashes", []):
            new_hashes.append(h)
    save_sent_history(history, new_hashes)

    logger.info("=" * 50)
    logger.info("Workflow completed successfully!")
    logger.info("=" * 50)
    return True


if __name__ == "__main__":
    # Parse arguments
    ai_mode = "--ai" in sys.argv or "-a" in sys.argv
    limit = 5
    for i, arg in enumerate(sys.argv):
        if arg.isdigit():
            limit = int(arg)

    success = run_workflow(ai_mode=ai_mode, limit=limit)
    sys.exit(0 if success else 1)