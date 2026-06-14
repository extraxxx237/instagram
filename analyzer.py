"""Analyzes scraped posts and extracts viral patterns."""

import json
import logging
import re
from collections import Counter
from datetime import datetime, timezone

from config import SCRAPED_FILE, ANALYSIS_FILE, MIN_VIRAL_SCORE

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def _days_since(iso_str: str | None) -> float:
    if not iso_str:
        return 30.0
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        return max(0.5, delta.total_seconds() / 86400)
    except ValueError:
        return 30.0


def viral_score(post: dict) -> float:
    likes = post.get("like_count", 0)
    comments = post.get("comment_count", 0)
    views = post.get("play_count") or post.get("view_count") or 0
    age_days = _days_since(post.get("taken_at"))
    return (likes + comments * 3 + views * 0.05) / age_days


def extract_hashtags(caption: str) -> list[str]:
    return re.findall(r"#(\w+)", caption.lower())


def analyze(posts: list[dict]) -> dict:
    for p in posts:
        p["viral_score"] = viral_score(p)

    qualified = [p for p in posts if p["viral_score"] >= MIN_VIRAL_SCORE]
    qualified.sort(key=lambda p: p["viral_score"], reverse=True)
    top_posts = qualified[:50]

    hashtag_counter: Counter = Counter()
    caption_lengths: list[int] = []
    hour_counter: Counter = Counter()
    theme_words: Counter = Counter()

    for p in top_posts:
        cap = p.get("caption", "")
        hashtag_counter.update(extract_hashtags(cap))
        caption_lengths.append(len(cap))

        taken = p.get("taken_at")
        if taken:
            try:
                dt = datetime.fromisoformat(taken)
                hour_counter[dt.hour] += 1
            except ValueError:
                pass

        words = re.findall(r"\b[a-zA-Z]{4,}\b", cap.lower())
        theme_words.update(w for w in words if w not in STOP_WORDS)

    avg_caption_len = int(sum(caption_lengths) / len(caption_lengths)) if caption_lengths else 200
    best_hours = [h for h, _ in hour_counter.most_common(5)]
    top_hashtags = [tag for tag, _ in hashtag_counter.most_common(30)]
    top_themes = [w for w, _ in theme_words.most_common(20)]

    analysis = {
        "total_scraped": len(posts),
        "qualified_posts": len(qualified),
        "top_posts": top_posts[:10],
        "top_hashtags": top_hashtags,
        "top_themes": top_themes,
        "avg_caption_length": avg_caption_len,
        "best_posting_hours": best_hours,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    log.info(
        "Analysis complete: %d qualified posts, top hashtags: %s",
        len(qualified),
        top_hashtags[:5],
    )
    return analysis


def run():
    with open(SCRAPED_FILE, encoding="utf-8") as f:
        posts = json.load(f)
    return analyze(posts)


STOP_WORDS = {
    "this", "that", "with", "from", "they", "have", "been", "will", "your",
    "more", "also", "into", "over", "just", "like", "some", "what", "when",
    "then", "than", "them", "their", "there", "these", "those", "make",
    "made", "here", "come", "could", "would", "should", "love", "grow",
    "growing", "great", "good", "best", "about", "after", "before",
}


if __name__ == "__main__":
    run()
