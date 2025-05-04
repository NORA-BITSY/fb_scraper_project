from sqlalchemy import Column, String, DateTime, Text, JSON, Index, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    post_id      = Column(String, primary_key=True)
    group_id     = Column(String, index=True)
    author_id    = Column(String)
    author_name  = Column(String)
    published_at = Column(DateTime)
    text         = Column(Text)
    images       = Column(JSON)
    scraped_at   = Column(DateTime, server_default=func.now())

    __table_args__ = (Index("ix_posts_text_gin", "text", postgresql_using="gin"),)
