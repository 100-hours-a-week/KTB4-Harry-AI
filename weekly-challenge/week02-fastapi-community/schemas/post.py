from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class SummaryResponse(BaseModel):
    summary: str = ""