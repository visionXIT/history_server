from typing import List, Optional
from pydantic import BaseModel


class AnswerResponse(BaseModel):
    id: int
    title: str
    after_title: Optional[str] = None
    photos_url: List[str] = []
    is_chosen: bool = False
    is_correct: Optional[bool] = None
    question_id: int

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    title: str
    description: str
    photos_url: List[str] = []
    is_answered: bool = False
    quiz_id: int
    answers: List[AnswerResponse] = []

    class Config:
        from_attributes = True


class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    photos_url: Optional[List[str]] = None
    preview_photo: Optional[str] = None
    questions: List[QuestionResponse] = []
    is_completed: bool = False

    class Config:
        from_attributes = True


class QuizIDResponse(QuizResponse):
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    title: str
    after_title: Optional[str] = None
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
    description: Optional[str] = None
    author: Optional[str] = None
    content_url: Optional[str] = None
    photo_url: Optional[str] = None


class MediaResponse(BaseModel):
    url: str
