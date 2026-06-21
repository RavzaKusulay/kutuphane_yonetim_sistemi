from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Header
from app.database.database import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse
from fastapi import HTTPException
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

def check_admin(user: User):
    if user.role not in ["admin", "librarian"]:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Sadece admin veya kütüphaneci işlem yapabilir."
        )

@router.post("/books", response_model=BookResponse)
def create_book(
        book: BookCreate,
        current_user: User = Depends(get_current_user), # Token'ı okuyup kullanıcıyı getirir
        db: Session = Depends(get_db)
):
    
    check_admin(current_user)
    
    
    new_book = Book(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        publish_year=book.publish_year,
        total_copies=book.total_copies,
        available_copies=book.total_copies
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@router.get("/books")
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@router.put("/books/{book_id}")
def update_book(
        book_id: int,
        book: BookCreate,
        db: Session = Depends(get_db)
):
    db_book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not db_book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    db_book.isbn = book.isbn
    db_book.title = book.title
    db_book.author = book.author
    db_book.publisher = book.publisher
    db_book.publish_year = book.publish_year
    db_book.total_copies = book.total_copies

    db.commit()

    return {
        "message": "Book updated"
    }

@router.delete("/books/{book_id}")
def delete_book(
        book_id: int,
        db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    db.delete(book)
    db.commit()

    return {
        "message": "Book deleted"
    }

@router.get("/books/search")
def search_books(
        keyword: str,
        db: Session = Depends(get_db)
):
    books = db.query(Book).filter(
        (Book.title.ilike(f"%{keyword}%")) |
        (Book.author.ilike(f"%{keyword}%")) |
        (Book.publisher.ilike(f"%{keyword}%")) |
        (Book.isbn.ilike(f"%{keyword}%"))
    ).all()

    return books