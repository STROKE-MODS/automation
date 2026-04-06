#!/usr/bin/env python3
"""
Demo script showing YouTube AI Digest usage.
Run this to see the project in action without needing API keys.
"""

import sys
import io
import subprocess
from pathlib import Path

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def run_command(cmd, description):
    """Run a command and display its output."""
    print(f"\n{'='*60}")
    print(f"[>] {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode


def main():
    """Run demo sequence."""
    print("""
+========================================================+
|         YouTube AI Digest - Demo                      |
|         Automated AI/ML Video Newsletter              |
+========================================================+
    """)

    # Demo 1: Scrape with test data
    run_command(
        [sys.executable, "scripts/scrape_youtube_trending.py", "3", "--test", "--ai"],
        "Step 1: Scrape AI/ML videos (test mode)"
    )

    # Demo 2: Generate summary
    run_command(
        [sys.executable, "scripts/generate_video_summary.py"],
        "Step 2: Generate AI summary"
    )

    # Demo 3: Format report
    run_command(
        [sys.executable, "scripts/format_trending_report.py", "3"],
        "Step 3: Format for Telegram"
    )

    # Show output
    print(f"\n{'='*60}")
    print("Generated Report (saved to .tmp/trending_report.txt):")
    print(f"{'='*60}")

    report_path = Path(".tmp/trending_report.txt")
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8", errors="replace")
        print(content)
    else:
        print("No report found")

    print(f"\n{'='*60}")
    print("[+] Demo Complete!")
    print(f"{'='*60}")
    print("""
To run with real data:
  1. Copy .env.example to .env
  2. Add your API keys
  3. Run: python scripts/run.py --ai
    """)


if __name__ == "__main__":
    main()