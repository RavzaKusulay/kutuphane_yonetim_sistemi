from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    isbn = Column(String, unique=True, nullable=False)

    title = Column(String, nullable=False)

    author = Column(String, nullable=False)

    publisher = Column(String)

    publish_year = Column(Integer)

    total_copies = Column(Integer, default=1)

    available_copies = Column(Integer, default=1)