"""Downloads thumbnail previews of top viral posts for reference/moodboard purposes only.

IMPORTANT: These images belong to their original creators and are NEVER used
for actual posting — only as visual reference to understand what styles/colors/
compositions perform well in the gardening niche. Actual posts use generated
graphics (poster.py) or your own photos (config.OWN_IMAGES_DIR).
"""

import json
import logging
import os

import requests

from config import ANALYSIS_FILE, REFERENCE_IMAGES_DIR

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def download_reference_thumbnails(limit: int = 10) -> list[str]:
    with open(ANALYSIS_FILE, encoding="utf-8") as f:
        analysis = json.load(f)

    saved_paths = []
    for i, post in enumerate(analysis.get("top_posts", [])[:limit]):
        url = post.get("thumbnail_url")
        if not url:
            continue

        dest = os.path.join(REFERENCE_IMAGES_DIR, f"ref_{i:02d}_{post['id']}.jpg")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                f.write(resp.content)
            saved_paths.append(dest)
            log.info("Saved reference thumbnail: %s (score=%.0f)", dest, post["viral_score"])
        except requests.RequestException as exc:
            log.warning("Failed to download %s: %s", url, exc)

    log.info("Saved %d reference thumbnails to %s", len(saved_paths), REFERENCE_IMAGES_DIR)
    return saved_paths


def run():
    return download_reference_thumbnails()


if __name__ == "__main__":
    run()
