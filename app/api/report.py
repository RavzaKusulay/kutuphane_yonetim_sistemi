from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import extract
from datetime import datetime

from app.database.database import get_db
from app.models.borrow_transaction import BorrowTransaction
from app.models.user import User
from app.models.book import Book

router = APIRouter()

@router.get("/reports/active-users")
def active_users(db: Session = Depends(get_db)):
    # Sadece durumu 'borrowed' olanlari getir ve kullanici/kitap bilgileriyle birlestir
    active_borrows = db.query(BorrowTransaction, User.username, Book.title)\
        .join(User, BorrowTransaction.user_id == User.id)\
        .join(Book, BorrowTransaction.book_id == Book.id)\
        .filter(BorrowTransaction.status == "borrowed").all()
    
    # Verileri kullanici ismine gore gruplayip, aldiklari kitaplari bir listeye koyalim
    user_data = {}
    for txn, username, title in active_borrows:
        if username not in user_data:
            user_data[username] = {"kullanici": username, "kitap_sayisi": 0, "kitaplar": []}
        user_data[username]["kitap_sayisi"] += 1
        user_data[username]["kitaplar"].append(title)
    
    # Frontend'in okuyabilmesi icin tablo (liste) formatina ceviriyoruz
    result = []
    for uname, data in user_data.items():
        result.append({
            "Kullanici Adi": data["kullanici"],
            "Aktif Odunc Sayisi": data["kitap_sayisi"],
            "Odunc Alinan Kitaplar": ", ".join(data["kitaplar"])
        })
    return result

@router.get("/reports/overdue")
def get_overdue_books(db: Session = Depends(get_db)):
    # Gecikmis kitaplari da kitap adi ve kullanici adi ile birlestiriyoruz
    overdue = db.query(BorrowTransaction, User.username, Book.title)\
        .join(User, BorrowTransaction.user_id == User.id)\
        .join(Book, BorrowTransaction.book_id == Book.id)\
        .filter(BorrowTransaction.status == "borrowed", BorrowTransaction.due_date < datetime.utcnow()).all()
    
    return [{
        "Kullanici Adi": username,
        "Kitap Adi": title,
        "Alis Tarihi": txn.borrow_date.strftime("%Y-%m-%d %H:%M"),
        "Son Teslim Tarihi": txn.due_date.strftime("%Y-%m-%d %H:%M")
    } for txn, username, title in overdue]

@router.get("/reports/most-borrowed")
def most_borrowed(db: Session = Depends(get_db)):
    # En cok odunc alinanlarda da ID yerine Kitap Adi donsun
    result = db.query(BorrowTransaction.book_id, Book.title, func.count(BorrowTransaction.book_id).label("count"))\
        .join(Book, BorrowTransaction.book_id == Book.id)\
        .group_by(BorrowTransaction.book_id, Book.title).all()
    
    return [{"Kitap Adi": row.title, "Odunc Alinma Sayisi": row.count} for row in result]

@router.get("/reports/currently-borrowed")
def currently_borrowed(db: Session = Depends(get_db)):
    return db.query(BorrowTransaction).filter(BorrowTransaction.status == "borrowed").all()

@router.get("/reports/monthly-stats")
def monthly_stats(db: Session = Depends(get_db)):
    result = db.query(
        extract("month", BorrowTransaction.borrow_date).label("month"),
        func.count(BorrowTransaction.id).label("total")
    ).group_by("month").all()
    return [{"Ay": row.month, "Toplam Islem": row.total} for row in result]