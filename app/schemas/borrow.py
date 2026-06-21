from pydantic import BaseModel


class BorrowRequest(BaseModel):
    user_id: int
    book_id: int