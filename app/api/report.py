from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import extract
from app.database.database import get_db
from app.models.borrow_transaction import BorrowTransaction
from app.models.user import User

router = APIRouter()

@router.get("/reports/active-users")
def active_users(
        db: Session = Depends(get_db)
):
    result = db.query(
        BorrowTransaction.user_id,
        func.count(
            BorrowTransaction.user_id
        ).label("borrow_count")
    ).group_by(
        BorrowTransaction.user_id
    ).all()

    return result

@router.get("/reports/currently-borrowed")
def currently_borrowed(
        db: Session = Depends(get_db)
):
    borrowed = db.query(
        BorrowTransaction
    ).filter(
        BorrowTransaction.status == "borrowed"
    ).all()

    return borrowed

@router.get("/reports/monthly-stats")
def monthly_stats(
        db: Session = Depends(get_db)
):
    result = db.query(
        extract(
            "month",
            BorrowTransaction.borrow_date
        ).label("month"),

        func.count(
            BorrowTransaction.id
        ).label("total")
    ).group_by(
        "month"
    ).all()

    return result

@router.get("/reports/most-borrowed")
def most_borrowed(
        db: Session = Depends(get_db)
):
    result = db.query(
        BorrowTransaction.book_id,
        func.count(
            BorrowTransaction.book_id
        ).label("count")
    ).group_by(
        BorrowTransaction.book_id
    ).all()

    return result

from datetime import datetime

@router.get("/reports/overdue")
def get_overdue_books(
        db: Session = Depends(get_db)
):
    # Status'ü 'borrowed' olan ve due_date'i bugünden küçük olanlar
    overdue_transactions = db.query(BorrowTransaction).filter(
        BorrowTransaction.status == "borrowed",
        BorrowTransaction.due_date < datetime.utcnow()
    ).all()

    return overdue_transactions