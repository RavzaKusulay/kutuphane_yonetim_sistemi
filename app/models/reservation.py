from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from datetime import datetime

from app.database.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    book_id = Column(Integer, ForeignKey("books.id"))

    reservation_date = Column(DateTime, default=datetime.utcnow)

    status = Column(String, default="active")