import os, asyncio, yaml
from celery import Celery
from fb_scraper.core.fb_login import ensure_login
from fb_scraper.core.scrolling import harvest_posts
from fb_scraper.core.parser import parse_article
from fb_scraper.db.init import Session, upsert_post
from fb_scraper.utils import log
from playwright.async_api import async_playwright

celery = Celery(
    "fb_tasks",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)
celery.conf.beat_schedule = {
    "nightly-scrape": {
        "task": "fb_scraper.core.tasks.scrape_all",
        "schedule": 60 * 60 * 24,
    }
}

@celery.task
def scrape_all():
    cfg = yaml.safe_load(open("scrape_config.yaml"))
    res = {gid: scrape_group.delay(url, gid).id for gid, url in cfg["groups"].items()}
    return res

@celery.task(bind=True)
def scrape_group(self, group_url: str, group_id: str) -> int:
    asyncio.run(ensure_login())
    added = 0
    async def runner():
        nonlocal added
        async with async_playwright() as p:
            ctx = await p.firefox.launch_persistent_context(
                os.getenv("USER_DATA_DIR", "/tmp/fb_profile"), headless=True
            )
            page = await ctx.new_page()
            await page.goto(group_url, timeout=45000)
            raw = await harvest_posts(page)
            sess = Session()
            for html in raw:
                post = parse_article(html, group_id)
                if post and upsert_post(sess, post):
                    added += 1
            await ctx.close()
            sess.close()
    asyncio.run(runner())
    log.info("Group %s ⟶ %d new/updated posts", group_id, added)
    return added
