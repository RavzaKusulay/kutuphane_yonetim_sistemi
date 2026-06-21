from pydantic import BaseModel


class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    publish_year: int
    total_copies: int


class BookResponse(BaseModel):
    id: int
    isbn: str
    title: str
    author: str
    publisher: str
    publish_year: int
    total_copies: int
    available_copies: int

    class Config:
        from_attributes = True