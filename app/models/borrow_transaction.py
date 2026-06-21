from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from datetime import datetime

from app.database.database import Base


class BorrowTransaction(Base):
    __tablename__ = "borrow_transactions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    book_id = Column(Integer, ForeignKey("books.id"))

    borrow_date = Column(DateTime, default=datetime.utcnow)

    due_date = Column(DateTime)

    return_date = Column(DateTime, nullable=True)

    status = Column(String, default="borrowed")