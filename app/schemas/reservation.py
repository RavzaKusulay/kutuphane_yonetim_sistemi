from pydantic import BaseModel


class ReservationRequest(BaseModel):
    user_id: int
    book_id: int