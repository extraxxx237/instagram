"""Generates new Instagram captions using Claude based on viral post patterns."""

import json
import logging
from datetime import datetime, timezone

import anthropic

from config import ANTHROPIC_API_KEY, ANALYSIS_FILE, GENERATED_FILE, CAPTION_VARIATIONS

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


SYSTEM_PROMPT = """You are an expert Instagram content creator specializing in gardening content.
You write engaging, authentic captions that drive high engagement (likes, comments, saves).
Your captions feel personal, inspiring, and informative — never salesy or robotic.
You always include a clear call-to-action and end with a curated hashtag block."""


def build_user_prompt(analysis: dict, variation_index: int) -> str:
    top_posts_examples = "\n\n".join(
        f"Post {i+1} (viral score: {p['viral_score']:.0f}):\n{p['caption'][:400]}"
        for i, p in enumerate(analysis.get("top_posts", [])[:5])
    )
    top_hashtags = " ".join(f"#{h}" for h in analysis.get("top_hashtags", [])[:20])
    themes = ", ".join(analysis.get("top_themes", [])[:10])
    avg_len = analysis.get("avg_caption_length", 200)

    styles = [
        "inspiring and motivational — share a gardening tip as a life lesson",
        "educational and practical — teach one specific gardening technique with step-by-step hints",
        "storytelling and personal — share a relatable gardening struggle or success moment",
    ]
    style = styles[variation_index % len(styles)]

    return f"""Here are today's top viral gardening posts for inspiration:

{top_posts_examples}

---
Top trending hashtags: {top_hashtags}
Trending themes: {themes}
Ideal caption length: ~{avg_len} characters

Write a NEW, ORIGINAL Instagram caption in this style: **{style}**

Requirements:
- Do NOT copy the example posts — write something fresh
- Caption body: {max(150, avg_len - 100)}–{avg_len + 100} characters (before hashtags)
- End with a strong call-to-action (question, "save this", "tag a friend", etc.)
- Include 15–25 relevant hashtags at the end (mix popular + niche)
- Use 3–5 relevant emojis naturally throughout
- Language: German (for a German-speaking gardening audience)

Return ONLY the caption text (no labels, no explanation)."""


def generate_captions(analysis: dict) -> list[dict]:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    captions = []

    for i in range(CAPTION_VARIATIONS):
        log.info("Generating caption variation %d/%d...", i + 1, CAPTION_VARIATIONS)
        prompt = build_user_prompt(analysis, i)

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        caption_text = message.content[0].text.strip()
        captions.append(
            {
                "id": f"gen_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{i}",
                "caption": caption_text,
                "variation": i,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "posted": False,
                "posted_at": None,
            }
        )
        log.info("  → Generated %d chars", len(caption_text))

    return captions


def run():
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("Set ANTHROPIC_API_KEY in .env")

    with open(ANALYSIS_FILE, encoding="utf-8") as f:
        analysis = json.load(f)

    try:
        with open(GENERATED_FILE, encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = []

    unposted = [p for p in existing if not p.get("posted")]
    if len(unposted) >= CAPTION_VARIATIONS:
        log.info("Enough unposted captions available (%d), skipping generation.", len(unposted))
        return existing

    new_captions = generate_captions(analysis)
    all_captions = existing + new_captions

    with open(GENERATED_FILE, "w", encoding="utf-8") as f:
        json.dump(all_captions, f, ensure_ascii=False, indent=2)

    log.info("Saved %d total captions to %s", len(all_captions), GENERATED_FILE)
    return all_captions


if __name__ == "__main__":
    run()
