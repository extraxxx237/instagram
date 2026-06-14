import os
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

TARGET_HASHTAGS = [
    tag.strip()
    for tag in os.getenv(
        "TARGET_HASHTAGS",
        "gardening,garden,plants,homegarden,urbangarden,gardenlife,gardeningtips,plantlover,greenthumb,vegetablegarden",
    ).split(",")
    if tag.strip()
]

POSTS_PER_HASHTAG = int(os.getenv("POSTS_PER_HASHTAG", "20"))
POST_TIMES = [t.strip() for t in os.getenv("POST_TIMES", "09:00,18:00").split(",") if t.strip()]
MAX_POSTS_PER_DAY = int(os.getenv("MAX_POSTS_PER_DAY", "2"))
MIN_VIRAL_SCORE = float(os.getenv("MIN_VIRAL_SCORE", "50"))
CAPTION_VARIATIONS = int(os.getenv("CAPTION_VARIATIONS", "3"))

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SCRAPED_FILE = os.path.join(DATA_DIR, "scraped_posts.json")
ANALYSIS_FILE = os.path.join(DATA_DIR, "analysis.json")
GENERATED_FILE = os.path.join(DATA_DIR, "generated_posts.json")
POSTED_LOG_FILE = os.path.join(DATA_DIR, "posted_log.json")
SESSION_FILE = os.path.join(DATA_DIR, "session.json")

os.makedirs(DATA_DIR, exist_ok=True)
