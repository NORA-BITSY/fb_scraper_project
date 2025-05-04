import os, logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fb_scraper.db.models import Base, Post

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        except Exception as e:
            logging.warning("Could not create extension pg_trgm: %s", e)
    logging.info("DB ready.")

def upsert_post(sess, p):
    existing = sess.get(Post, p.post_id)
    changed = False
    if existing:
        if existing.text != p.text:
            existing.text = p.text
            changed = True
    else:
        sess.add(Post(**p.dict()))
        changed = True
    if changed:
        sess.commit()
    return changed
