from typing import List, Annotated
from sqlalchemy import Column, ForeignKey, Enum, ARRAY, String, Table
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import enum

PrimaryKey = Annotated[int, mapped_column(primary_key=True, index=True)]
StrList = List[str]


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[PrimaryKey]


stats_answers_association = Table(
    "stats_answers",
    Base.metadata,
    Column("stats_id", ForeignKey("stats.id"), primary_key=True),
    Column("answer_id", ForeignKey("answers.id"), primary_key=True))


class Answer(BaseModel):
    __tablename__ = 'answers'

    title: Mapped[str] = mapped_column(nullable=False)
    after_title: Mapped[str] = mapped_column(nullable=False)
    photos_url: Mapped[List[str] | None] = mapped_column(
        ARRAY(String), nullable=True)
    is_correct: Mapped[bool | None]
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))

    question: Mapped["Question"] = relationship(back_populates='answers')

    stats: Mapped[List["Stats"]] = relationship(
        "Stats", secondary=stats_answers_association, back_populates="correct_answers"
    )


class Question(BaseModel):
    __tablename__ = 'questions'

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    photos_url: Mapped[List[str] | None] = mapped_column(
        ARRAY(String), nullable=True)

    answers: Mapped[List["Answer"]] = relationship(back_populates='question')
    quiz: Mapped["Quiz"] = relationship(back_populates='questions')


class Quiz(BaseModel):
    __tablename__ = 'quizzes'

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    photos_url: Mapped[List[str] | None] = mapped_column(
        ARRAY(String), nullable=True)
    preview_photo: Mapped[str | None]

    questions: Mapped[List["Question"]] = relationship(back_populates='quiz')
    stats: Mapped[List["Stats"]] = relationship(back_populates='quiz')


class UserQuizAnswer(BaseModel):
    __tablename__ = 'user_quiz_answer'

    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))
    user_id: Mapped[str] = mapped_column(nullable=False)


class Stats(BaseModel):
    __tablename__ = 'stats'

    user_id: Mapped[str] = mapped_column(nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    correct_answers: Mapped[List["Answer"]] = relationship(
        "Answer", secondary=stats_answers_association, back_populates="stats"
    )

    quiz: Mapped["Quiz"] = relationship(back_populates='stats')


class ArticleStatus(enum.Enum):
    __tablename__ = "article_status"
    PUBLISHED = "published"
    DRAFT = "draft"


class Article(BaseModel):
    __tablename__ = 'articles'

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    content_url: Mapped[str | None]
    photo_url: Mapped[str | None]
    author: Mapped[str | None]
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus, name="article_status"),
        nullable=False,
        default=ArticleStatus.DRAFT
    )


class GalleryPhoto(BaseModel):
    __tablename__ = 'gallery_photos'

    id: Mapped[PrimaryKey]
    title: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    order: Mapped[int] = mapped_column(default=0)
    url: Mapped[str] = mapped_column(nullable=False)
