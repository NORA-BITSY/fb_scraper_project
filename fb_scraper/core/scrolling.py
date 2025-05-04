async def harvest_posts(page, how_far: int = 5):
    posts = set()
    for _ in range(how_far):
        await page.wait_for_selector("article", timeout=10000)
        posts |= set(await page.locator("article").all_inner_html())
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
    return list(posts)
