from typing import List
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from app.models import Answer, ArticleStatus, Quiz, UserQuizAnswer, Question, Article
from app.schemas import QuizResponse, ArticleResponse, QuizIDResponse
from app.database import get_db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, Session

app = FastAPI()

# Add this after FastAPI initialization
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_user_id(authorization: str | None = Security(api_key_header)) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Необходима регистрация")
    return authorization


@app.get('/quiz', response_model=List[QuizResponse])
def get_quizes(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    quizes = db.query(Quiz).all()
    return quizes


@app.get('/quiz/{quiz_id}', response_model=QuizResponse)
def get_quiz(quiz_id: int, user_id: str = Depends(get_user_id), db: Session = Depends(get_db)):
    print(user_id)
    quiz = db.query(Quiz).options(joinedload(Quiz.questions)
                                  ).filter(Quiz.id == quiz_id).first()

    if quiz is None:
        raise HTTPException(status_code=404, detail="Викторина не найдена")

    user_answers = db.query(UserQuizAnswer).join(Answer).join(Question).filter(
        UserQuizAnswer.user_id == user_id, Question.quiz_id == quiz_id).all()

    quiz_completed = len(user_answers) == len(quiz.questions)

    return QuizIDResponse(title=quiz.title, text=quiz.description, is_completed=quiz_completed, questions=quiz.questions, photos_url=quiz.photos_url, preview_photo=quiz.preview_photo)


@app.post('/answer/{answer_id}')
def submit_answer(answer_id: int, user_id: str = Depends(get_user_id), db: Session = Depends(get_db)):
    if db.query(UserQuizAnswer).filter_by(user_id=user_id, answer_id=answer_id).first():
        raise HTTPException(status_code=400, detail="Ответ уже дан")

    if db.query(Answer).filter_by(id=answer_id).first() is None:
        raise HTTPException(
            status_code=404, detail="Ответ на вопрос не найден")

    user_answer = UserQuizAnswer(user_id=user_id, answer_id=answer_id)

    try:
        db.add(user_answer)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка сохранения ответа")

    return {"status": "success"}


@app.get('/article', response_model=List[ArticleResponse])
def get_articles(db: Session = Depends(get_db)):
    articles = db.query(Article).filter(
        Article.status == ArticleStatus.PUBLISHED).all()
    return articles


@app.post('/article')
def create_article(article: ArticleResponse, db: Session = Depends(get_db)):
    article = Article(**article.model_dump(), status=ArticleStatus.DRAFT)
    db.add(article)
    db.commit()
    return article


@app.get('/article/{article_id}', response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(
        Article.id == article_id, Article.status == ArticleStatus.PUBLISHED).first()
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article
