from typing import List, Optional
from pydantic import BaseModel


class AnswerResponse(BaseModel):
    id: int
    title: str
    after_title: Optional[str] = None
    photos_url: List[str] | None = None
    is_chosen: bool = False
    is_correct: Optional[bool] = None

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    photos_url: List[str] | None = None
    is_answered: bool = False
    answers: List[AnswerResponse] = []

    class Config:
        from_attributes = True


class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    photos_url: Optional[List[str]] = None
    preview_photo: Optional[str] = None
    is_completed: bool = False

    class Config:
        from_attributes = True


class QuizIDResponse(QuizResponse):
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    title: str
    after_title: str
    photos_url: Optional[List[str]]
    is_correct: bool


class QuestionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    photos_url: Optional[List[str]] = None
    answers: List[AnswerCreate] = []


class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    photos_url: Optional[List[str]] = None
    preview_photo: Optional[str] = None
    questions: List[QuestionCreate] = []


class ArticleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    content_url: Optional[str] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class ArticleCreateBody(BaseModel):
    title: str
    description: str | None = None
    author: str | None = None
    content_url: str | None = None
    photo_url: str | None = None


class ArticleUpdateBody(BaseModel):
    title: str | None = None
    description: str | None = None
    author: str | None = None
    content_url: str | None = None
    photo_url: str | None = None


class MediaResponse(BaseModel):
    url: str


class AnswerStatsResponse(BaseModel):
    id: int
    title: str
    count: int

    class Config:
        from_attributes = True


class QuestionStatsResponse(BaseModel):
    question_id: int
    question_title: str
    correct_answers: int
    incorrect_answers: int
    answers: List[AnswerStatsResponse] = []

    class Config:
        from_attributes = True


class QuizStatsResponse(BaseModel):
    questions: List[QuestionStatsResponse] = []

    class Config:
        from_attributes = True


class GalleryPhotoCreate(BaseModel):
    title: str | None = None
    description: str | None = None
    order: int = 0


class GalleryPhotoResponse(BaseModel):
    id: int
    title: str | None
    description: str | None
    order: int
    media_items: List[MediaResponse]

    class Config:
        from_attributes = True
