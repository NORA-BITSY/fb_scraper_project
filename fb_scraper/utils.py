import logging, time
from contextlib import contextmanager

log = logging.getLogger("fb_scraper")

@contextmanager
def elapsed(msg: str):
    start = time.perf_counter()
    yield
    log.info("%s – %.2f s", msg, time.perf_counter() - start)
