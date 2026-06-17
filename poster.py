"""Posts generated content to Instagram via instagrapi."""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
from instagrapi.exceptions import ClientError

from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    GENERATED_FILE,
    POSTED_LOG_FILE,
    SESSION_FILE,
    DATA_DIR,
    OWN_IMAGES_DIR,
)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PLACEHOLDER_IMG = os.path.join(DATA_DIR, "placeholder.jpg")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def build_client() -> Client:
    from scraper import build_client as _build
    return _build()


def _next_own_image() -> str | None:
    """Returns the oldest unused image from OWN_IMAGES_DIR, if any."""
    candidates = sorted(
        f for f in os.listdir(OWN_IMAGES_DIR)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    )
    if not candidates:
        return None
    return os.path.join(OWN_IMAGES_DIR, candidates[0])


def _archive_own_image(path: str):
    """Moves a used own-image into a 'used' subfolder so it isn't reposted."""
    used_dir = os.path.join(OWN_IMAGES_DIR, "used")
    os.makedirs(used_dir, exist_ok=True)
    os.rename(path, os.path.join(used_dir, os.path.basename(path)))


def _create_placeholder_image(caption_snippet: str) -> str:
    img = Image.new("RGB", (1080, 1080), color=(45, 110, 60))
    draw = ImageDraw.Draw(img)

    for y in range(1080):
        alpha = int(30 * (y / 1080))
        draw.line([(0, y), (1080, y)], fill=(20 + alpha, 80 + alpha, 40 + alpha))

    text = caption_snippet[:80] + "..." if len(caption_snippet) > 80 else caption_snippet
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except OSError:
        font = ImageFont.load_default()

    draw.text((80, 480), text, fill=(255, 255, 255), font=font)
    draw.text((80, 60), "🌱", fill=(200, 255, 200), font=font)

    img.save(PLACEHOLDER_IMG, "JPEG", quality=95)
    return PLACEHOLDER_IMG


def load_next_unposted() -> dict | None:
    try:
        with open(GENERATED_FILE, encoding="utf-8") as f:
            posts = json.load(f)
    except FileNotFoundError:
        return None

    for post in posts:
        if not post.get("posted"):
            return post
    return None


def mark_as_posted(post_id: str, instagram_media_id: str | None = None):
    with open(GENERATED_FILE, encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        if post["id"] == post_id:
            post["posted"] = True
            post["posted_at"] = datetime.now(timezone.utc).isoformat()
            post["instagram_media_id"] = instagram_media_id
            break

    with open(GENERATED_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    try:
        with open(POSTED_LOG_FILE, encoding="utf-8") as f:
            log_entries = json.load(f)
    except FileNotFoundError:
        log_entries = []

    log_entries.append(
        {
            "post_id": post_id,
            "instagram_media_id": instagram_media_id,
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    with open(POSTED_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_entries, f, ensure_ascii=False, indent=2)


def post_to_instagram(image_path: str | None = None) -> bool:
    post = load_next_unposted()
    if not post:
        log.info("No unposted captions available. Run 'generate' first.")
        return False

    caption = post["caption"]
    own_image = None
    if not image_path:
        own_image = _next_own_image()
    img_path = image_path or own_image or _create_placeholder_image(caption)

    log.info("Posting caption (id=%s)...", post["id"])
    log.info("Caption preview: %s...", caption[:100])
    log.info("Image source: %s", "own photo" if own_image else ("custom path" if image_path else "generated placeholder"))

    cl = build_client()
    media_id = None

    for attempt in range(3):
        try:

            media = cl.photo_upload(img_path, caption=caption)
            media_id = str(media.pk)
            log.info("Posted successfully! Media ID: %s", media_id)
            break
        except ClientError as exc:
            log.error("Upload attempt %d failed: %s", attempt + 1, exc)
            if attempt < 2:
                time.sleep(2 ** (attempt + 2))
            else:
                log.error("All upload attempts failed.")
                return False

    mark_as_posted(post["id"], media_id)
    if own_image and media_id:
        _archive_own_image(own_image)
    return True


def run(image_path: str | None = None):
    return post_to_instagram(image_path)


if __name__ == "__main__":
    import sys
    img = sys.argv[1] if len(sys.argv) > 1 else None
    run(img)
