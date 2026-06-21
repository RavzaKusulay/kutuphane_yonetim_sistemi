from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.book import Book
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationRequest

router = APIRouter()


@router.post("/reserve")
def reserve_book(
        request: ReservationRequest,
        db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.id == request.book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    # kitap varsa reserve etmesin
    if book.available_copies > 0:
        raise HTTPException(
            status_code=400,
            detail="Book available, no need reservation"
        )

    # duplicate reservation kontrol
    existing = db.query(Reservation).filter(
        Reservation.user_id == request.user_id,
        Reservation.book_id == request.book_id,
        Reservation.status == "active"
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already reserved"
        )

    reservation = Reservation(
        user_id=request.user_id,
        book_id=request.book_id,
        status="active"
    )

    db.add(reservation)
    db.commit()

    return {
        "message": "Reservation created"
    }