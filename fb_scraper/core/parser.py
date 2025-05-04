import re
from bs4 import BeautifulSoup
from datetime import datetime
from pydantic import BaseModel, HttpUrl

_PATTERNS = (r'feed_story_(\d+)"', r'top_level_post_id&quot;:&quot;(\d+)')

class Post(BaseModel):
    post_id: str
    group_id: str
    author_id: str | None
    author_name: str | None
    published_at: datetime
    text: str
    images: list[HttpUrl] = []

def parse_article(html: str, group_id: str) -> Post | None:
    soup = BeautifulSoup(html, "lxml")
    art = soup.select_one("article")
    if not art:
        return None
    post_id = None
    for pat in _PATTERNS:
        m = re.search(pat, html)
        if m:
            post_id = m.group(1)
            break
    if not post_id:
        return None
    author_tag = art.select_one("h3 a")
    author_name = author_tag.text.strip() if author_tag else None
    author_id = author_tag["href"].split("facebook.com/")[-1].split("?")[0] if author_tag else None
    span = art.select_one("a[aria-label][tabindex='0'] span")
    ts = datetime.utcfromtimestamp(int(span["data-utime"])) if span and span.has_attr("data-utime") else datetime.utcnow()
    text = " ".join(e.get_text(" ", strip=True) for e in art.select("div[dir='auto']"))
    imgs = [img["src"] for img in art.select("img") if "scontent" in img.get("src", "")]
    return Post(post_id=post_id, group_id=group_id, author_id=author_id, author_name=author_name,
                published_at=ts, text=text, images=imgs)
