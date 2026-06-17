#!/usr/bin/env python3
"""
Instagram Gardening Content Automation - Main CLI

Usage:
    python workflow.py scrape       Scrape viral gardening posts from Instagram
    python workflow.py analyze      Analyze scraped posts and extract patterns
    python workflow.py generate     Generate new captions with Claude AI
    python workflow.py post [IMG]   Post next caption (optional: path to image)
    python workflow.py status       Show pipeline status
    python workflow.py run          Run full automated loop (scheduler)
    python workflow.py once         Run one full cycle: scrape->analyze->generate->post
    python workflow.py references   Download viral post thumbnails for moodboard reference
    python workflow.py dashboard    Launch web dashboard to review/approve posts
"""

import json
import logging
import sys
from pathlib import Path

from config import SCRAPED_FILE, ANALYSIS_FILE, GENERATED_FILE, POSTED_LOG_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def cmd_scrape():
    import scraper
    posts = scraper.run()
    print(f"\n✅  Scraped {len(posts)} posts → {SCRAPED_FILE}")


def cmd_analyze():
    import analyzer
    analysis = analyzer.run()
    print(f"\n✅  Analyzed posts.")
    print(f"    Qualified: {analysis['qualified_posts']}")
    print(f"    Top hashtags: {' '.join('#' + h for h in analysis['top_hashtags'][:10])}")
    print(f"    Avg caption length: {analysis['avg_caption_length']} chars")
    print(f"    Best posting hours: {analysis['best_posting_hours']}")


def cmd_generate():
    import generator
    captions = generator.run()
    unposted = [c for c in captions if not c.get("posted")]
    print(f"\n✅  Generated captions. Unposted queue: {len(unposted)}")
    if unposted:
        print(f"\n--- Next caption preview ---\n{unposted[0]['caption'][:200]}...\n")


def cmd_post(image_path: str | None = None):
    import poster
    success = poster.run(image_path)
    if success:
        print("\n✅  Posted successfully!")
    else:
        print("\n❌  Nothing to post or upload failed. Check logs.")


def cmd_status():
    def load(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    scraped = load(SCRAPED_FILE)
    analysis = load(ANALYSIS_FILE)
    generated = load(GENERATED_FILE)
    posted_log = load(POSTED_LOG_FILE)

    print("\n📊  Pipeline Status")
    print("─" * 40)
    print(f"  Scraped posts:      {len(scraped) if scraped else '—'}")
    print(f"  Qualified posts:    {analysis['qualified_posts'] if analysis else '—'}")
    if analysis:
        print(f"  Last analysis:      {analysis.get('analyzed_at', '—')[:19]}")
    if generated:
        unposted = [p for p in generated if not p.get("posted")]
        print(f"  Generated captions: {len(generated)} total, {len(unposted)} unposted")
    else:
        print(f"  Generated captions: —")
    print(f"  Total posts sent:   {len(posted_log) if posted_log else 0}")
    if posted_log:
        print(f"  Last posted:        {posted_log[-1]['posted_at'][:19]}")
    print()


def cmd_once():
    log.info("Running full cycle...")
    import scraper, analyzer, generator, poster
    posts = scraper.run()
    analysis = analyzer.analyze(posts)
    generator.run()
    poster.run()
    print("\n✅  Full cycle complete.")


def cmd_run():
    import scheduler
    scheduler.run()


def cmd_references():
    import reference_images
    paths = reference_images.run()
    print(f"\n✅  Downloaded {len(paths)} reference thumbnails (moodboard only, not for reposting).")


def cmd_dashboard():
    import dashboard
    print("\n🌱  Dashboard running at http://localhost:5000")
    dashboard.run()


COMMANDS = {
    "scrape": cmd_scrape,
    "analyze": cmd_analyze,
    "generate": cmd_generate,
    "status": cmd_status,
    "once": cmd_once,
    "run": cmd_run,
    "references": cmd_references,
    "dashboard": cmd_dashboard,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS and sys.argv[1] != "post":
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "post":
        img = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_post(img)
    else:
        COMMANDS[cmd]()


if __name__ == "__main__":
    main()
