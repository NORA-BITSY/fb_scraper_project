from fb_scraper.core.parser import parse_article

def test_parse_dummy():
    dummy_html = (
        '<article data-ft="{&quot;feed_story_id&quot;:&quot;feed_story_123&quot;}">'
        '<h3><a href="https://www.facebook.com/john.doe">John Doe</a></h3>'
        '<a aria-label="Tuesday" tabindex="0"><span data-utime="1714696800"></span></a>'
        '<div dir="auto">Hello world</div></article>'
    )
    post = parse_article(dummy_html, "group1")
    assert post.post_id == "123"
    assert post.text == "Hello world"
