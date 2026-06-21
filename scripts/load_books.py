import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import pandas as pd
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.book import Book


def load_books():

    # ; separator çünkü csv noktalı virgül kullanıyor
    df = pd.read_csv(
    "books_data/books.csv",
    sep=";",
    encoding="latin-1",
    on_bad_lines="skip"
)

    print("CSV loaded")

    db: Session = SessionLocal()

    imported = 0

    for _, row in df.iterrows():

        isbn = str(row["ISBN"]).strip()

        # duplicate kontrol
        existing = db.query(Book).filter(
            Book.isbn == isbn
        ).first()

        if existing:
            continue

        # year bazen string geliyor, güvenli parse
        try:
            year = int(row["Year-Of-Publication"])
        except:
            year = 0

        book = Book(
            isbn=isbn,
            title=str(row["Book-Title"]),
            author=str(row["Book-Author"]),
            publisher=str(row["Publisher"]),
            publish_year=year,
            total_copies=3,
            available_copies=3
        )

        db.add(book)
        imported += 1

        # performans için her 500 kayıtta commit
        if imported % 500 == 0:
            db.commit()
            print(f"{imported} books imported...")

    db.commit()
    db.close()

    print(f"Finished. Imported {imported} books")


load_books()