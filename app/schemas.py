from typing import List, Optional
from pydantic import BaseModel, ValidationInfo, field_validator


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

    @field_validator('is_correct', mode='before')
    def check_is_correct(cls, value: bool):
        if not value:
            return None
        return value

    @field_validator('after_title', mode='before')
    def check_after_title(cls, value, info: ValidationInfo):
        if not info.data.get('is_chosen'):
            return None
        return value


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
    questions: List[QuestionResponse] = []
    photos_url: Optional[List[str]] = None
    preview_photo: Optional[str] = None
    is_completed: bool = False

    class Config:
        from_attributes = True


class QuizIDResponse(BaseModel):
    title: str
    description: Optional[str] = None
    questions: List[QuestionResponse] = []
    photos_url: Optional[List[str]] = None
    preview_photo: Optional[str] = None
    questions: List[QuestionResponse] = []
    is_completed: bool = False

    class Config:
        from_attributes = True


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
