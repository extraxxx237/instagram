"""APScheduler-based daily scheduler for scraping, generating, and posting."""

import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import POST_TIMES, MAX_POSTS_PER_DAY

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

scheduler = BlockingScheduler(timezone="Europe/Berlin")
_posts_today = {"count": 0, "date": None}


def _reset_daily_counter():
    today = datetime.now().date()
    if _posts_today["date"] != today:
        _posts_today["count"] = 0
        _posts_today["date"] = today


def job_scrape_and_prepare():
    log.info("=== Daily prep job starting ===")
    try:
        import scraper
        import analyzer
        import generator
        posts = scraper.run()
        analysis = analyzer.analyze(posts)
        generator.run()
        log.info("=== Daily prep complete ===")
    except Exception as exc:
        log.error("Daily prep failed: %s", exc, exc_info=True)


def job_post():
    _reset_daily_counter()
    if _posts_today["count"] >= MAX_POSTS_PER_DAY:
        log.info("Daily post limit (%d) reached, skipping.", MAX_POSTS_PER_DAY)
        return

    try:
        import poster
        success = poster.run()
        if success:
            _posts_today["count"] += 1
            log.info("Post %d/%d today done.", _posts_today["count"], MAX_POSTS_PER_DAY)
    except Exception as exc:
        log.error("Post job failed: %s", exc, exc_info=True)


def setup_jobs():
    scheduler.add_job(job_scrape_and_prepare, CronTrigger(hour=6, minute=0), id="daily_prep")

    for i, time_str in enumerate(POST_TIMES):
        h, m = map(int, time_str.split(":"))
        scheduler.add_job(
            job_post,
            CronTrigger(hour=h, minute=m),
            id=f"post_{i}",
        )
        log.info("Scheduled post job at %s", time_str)


def run():
    setup_jobs()
    log.info("Scheduler started. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Scheduler stopped.")


if __name__ == "__main__":
    run()
