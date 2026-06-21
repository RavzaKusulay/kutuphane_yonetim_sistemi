from fastapi import FastAPI
from app.database.database import engine, Base
from app.api.book import router as book_router
from app.api.borrow import router as borrow_router
from app.api.reservation import router as reservation_router
from app.api.report import router as report_router

import app.models

from app.api.user import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)
app.include_router(book_router)
app.include_router(borrow_router)
app.include_router(reservation_router)
app.include_router(report_router)

@app.get("/")
def home():
    return {"message": "Library API working"}