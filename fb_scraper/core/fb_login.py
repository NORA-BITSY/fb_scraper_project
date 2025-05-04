import os, asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from fb_scraper.utils import log

COOKIE_FILE = Path(os.getenv("PLAYWRIGHT_STATE", "/data/fb_cookies.json"))
PROFILE_DIR = os.getenv("USER_DATA_DIR", "/tmp/fb_profile")

async def ensure_login() -> None:
    async with async_playwright() as p:
        ctx = await p.firefox.launch_persistent_context(PROFILE_DIR, headless=True)
        page = await ctx.new_page()
        await page.goto("https://www.facebook.com/")
        if "login" in page.url:
            await page.fill('input[name="email"]', os.getenv("FB_EMAIL"))
            await page.fill('input[name="pass"]', os.getenv("FB_PASSWORD"))
            await page.click('button[name="login"]')
            await page.wait_for_selector('[role="feed"]', timeout=15000)
            await ctx.storage_state(path=str(COOKIE_FILE))
            log.info("Logged-in & cookies saved.")
        await ctx.close()
