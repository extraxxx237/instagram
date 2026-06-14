"""Scrapes viral gardening posts from Instagram via instagrapi."""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError

from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    TARGET_HASHTAGS,
    POSTS_PER_HASHTAG,
    SCRAPED_FILE,
    SESSION_FILE,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def build_client() -> Client:
    cl = Client()
    cl.delay_range = [2, 5]  # polite delay between requests

    session_path = Path(SESSION_FILE)
    if session_path.exists():
        try:
            cl.load_settings(session_path)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            cl.get_timeline_feed()  # verify session is alive
            log.info("Reused existing session.")
            return cl
        except Exception:
            log.warning("Cached session invalid, logging in fresh.")

    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    cl.dump_settings(session_path)
    log.info("Logged in and session saved.")
    return cl


def _media_to_dict(media) -> dict:
    taken_at = media.taken_at
    if taken_at and taken_at.tzinfo is None:
        taken_at = taken_at.replace(tzinfo=timezone.utc)

    return {
        "id": str(media.pk),
        "code": media.code,
        "url": f"https://www.instagram.com/p/{media.code}/",
        "media_type": media.media_type,  # 1=photo, 2=video/reel, 8=carousel
        "caption": media.caption_text or "",
        "like_count": media.like_count or 0,
        "comment_count": media.comment_count or 0,
        "play_count": getattr(media, "play_count", None) or 0,
        "view_count": getattr(media, "view_count", None) or 0,
        "taken_at": taken_at.isoformat() if taken_at else None,
        "thumbnail_url": str(media.thumbnail_url) if media.thumbnail_url else None,
        "user_id": str(media.user.pk) if media.user else None,
        "username": media.user.username if media.user else None,
        "usertags": [str(t) for t in (media.usertags or [])],
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape_hashtags(cl: Client, hashtags: list[str], per_tag: int) -> list[dict]:
    results: list[dict] = []
    seen_ids: set[str] = set()

    for tag in hashtags:
        log.info("Scraping hashtag: #%s", tag)
        try:
            top_medias = cl.hashtag_medias_top(tag, amount=per_tag)
            recent_medias = cl.hashtag_medias_recent(tag, amount=max(5, per_tag // 4))
            medias = top_medias + recent_medias
        except (LoginRequired, ClientError) as exc:
            log.error("Error scraping #%s: %s", tag, exc)
            time.sleep(10)
            continue

        for media in medias:
            mid = str(media.pk)
            if mid in seen_ids:
                continue
            seen_ids.add(mid)
            post = _media_to_dict(media)
            post["source_hashtag"] = tag
            results.append(post)

        log.info("  → %d posts collected (total: %d)", len(medias), len(results))
        time.sleep(3)

    return results


def run():
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        raise RuntimeError("Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env")

    cl = build_client()
    posts = scrape_hashtags(cl, TARGET_HASHTAGS, POSTS_PER_HASHTAG)

    with open(SCRAPED_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    log.info("Saved %d posts to %s", len(posts), SCRAPED_FILE)
    return posts


if __name__ == "__main__":
    run()
