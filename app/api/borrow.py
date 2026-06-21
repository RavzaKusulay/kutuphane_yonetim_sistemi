from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.database import get_db
from app.models.book import Book
from app.models.borrow_transaction import BorrowTransaction
from app.schemas.borrow import BorrowRequest

router = APIRouter()


@router.post("/borrow")
def borrow_book(
        request: BorrowRequest,
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

    if book.available_copies <= 0:
        raise HTTPException(
            status_code=400,
            detail="Book unavailable"
        )

    transaction = BorrowTransaction(
        user_id=request.user_id,
        book_id=request.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status="borrowed"
    )

    book.available_copies -= 1

    db.add(transaction)
    db.commit()

    return {
        "message": "Book borrowed successfully"
    }

@router.post("/return")
def return_book(
        request: BorrowRequest,
        db: Session = Depends(get_db)
):
    transaction = db.query(
        BorrowTransaction
    ).filter(
        BorrowTransaction.user_id == request.user_id,
        BorrowTransaction.book_id == request.book_id,
        BorrowTransaction.status == "borrowed"
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="No active borrow found"
        )

    book = db.query(Book).filter(
        Book.id == request.book_id
    ).first()

    transaction.status = "returned"
    transaction.return_date = datetime.utcnow()

    book.available_copies += 1

    db.commit()

    return {
        "message": "Book returned successfully"
    }