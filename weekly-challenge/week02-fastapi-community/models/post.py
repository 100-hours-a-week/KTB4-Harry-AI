from sqlalchemy import Column, DateTime, Integer, String, Text

from database.base import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    post_date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=True)