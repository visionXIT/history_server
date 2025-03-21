from typing import List
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File
from fastapi.security import APIKeyHeader
from app.models import Answer, ArticleStatus, Quiz, UserQuizAnswer, Question, Article, Stats
from app.schemas import AnswerResponse, QuestionResponse, QuizCreate, QuizResponse, ArticleResponse, MediaResponse, ArticleCreateBody
from app.database import get_db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, Session
from app.media import s3_service

app = FastAPI()

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_user_id(authorization: str | None = Security(api_key_header)) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Необходима регистрация")
    return authorization


@app.get('/quiz', response_model=List[QuizResponse])
def get_quizes(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    quizes = db.query(Quiz).options(joinedload(
        Quiz.questions).joinedload(Question.answers)).all()
    quiz_responses = []

    for quiz in quizes:
        user_answers = db.query(UserQuizAnswer).join(Answer).join(Question).filter(
            UserQuizAnswer.user_id == user_id, Question.quiz_id == quiz.id).all()

        quiz_completed = len(user_answers) == len(quiz.questions)

        questions_response = []
        for question in quiz.questions:
            question_answered = any(
                ua.answer_id in [a.id for a in question.answers] for ua in user_answers)
            answers_response = [
                AnswerResponse(
                    id=answer.id,
                    title=answer.title,
                    after_title=answer.after_title,
                    photos_url=answer.photos_url,
                    is_chosen=any(ua.answer_id ==
                                  answer.id for ua in user_answers),
                    is_correct=answer.is_correct,
                    question_id=answer.question_id
                )
                for answer in question.answers
            ]
            questions_response.append(
                QuestionResponse(
                    id=question.id,
                    title=question.title,
                    description=question.description,
                    photos_url=question.photos_url,
                    is_answered=question_answered,
                    quiz_id=question.quiz_id,
                    answers=answers_response
                )
            )

        quiz_responses.append(QuizResponse(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            is_completed=quiz_completed,
            questions=questions_response,
            photos_url=quiz.photos_url,
            preview_photo=quiz.preview_photo
        ))

    return quiz_responses


@app.post('/quiz')
def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):

    if len(quiz.questions) < 1:
        raise HTTPException(
            status_code=400, detail="Викторина должна содержать хотя бы 1 вопрос")
    for question in quiz.questions:
        if len(question.answers) < 1:
            raise HTTPException(
                status_code=400, detail="На вопрос необходим хотя бы 1 ответ")

    new_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        photos_url=quiz.photos_url,
        preview_photo=quiz.preview_photo,
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    for question in quiz.questions:
        new_question = Question(
            title=question.title,
            description=question.description,
            photos_url=question.photos_url,
            quiz_id=new_quiz.id
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)

        for answer in question.answers:
            new_answer = Answer(
                title=answer.title,
                after_title=answer.after_title,
                photos_url=answer.photos_url,
                is_correct=answer.is_correct,
                question_id=new_question.id
            )
            db.add(new_answer)
            db.commit()
            db.refresh(new_answer)
    return new_quiz


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

    return QuizResponse(id=quiz.id, title=quiz.title, text=quiz.description, is_completed=quiz_completed, questions=quiz.questions, photos_url=quiz.photos_url, preview_photo=quiz.preview_photo)


@app.post('/answer/{answer_id}')
def submit_answer(answer_id: int, user_id: str = Depends(get_user_id), db: Session = Depends(get_db)):
    if db.query(Answer).filter_by(id=answer_id).first() is None:
        raise HTTPException(
            status_code=404, detail="Ответ на вопрос не найден")

    question = db.query(Question).join(
        Answer).filter(Answer.id == answer_id).first()
    question_answers = [answer.id for answer in question.answers]

    if db.query(UserQuizAnswer).filter(UserQuizAnswer.answer_id.in_(question_answers), UserQuizAnswer.user_id == user_id).first():
        raise HTTPException(status_code=400, detail="Ответ уже дан")

    user_answer = UserQuizAnswer(user_id=user_id, answer_id=answer_id)

    try:
        db.add(user_answer)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка сохранения ответа")

    quiz = db.query(Quiz).join(Question).join(
        Answer).filter(Answer.id == answer_id).first()

    user_answers = db.query(UserQuizAnswer).join(Answer).join(Question).filter(
        UserQuizAnswer.user_id == user_id, Question.quiz_id == quiz.id).all()

    if len(user_answers) == len(quiz.questions):
        correct_answers = db.query(Answer).join(Question).filter(
            Question.quiz_id == quiz.id, Answer.is_correct == True).all()
        stats = Stats(user_id=user_id, quiz_id=quiz.id, correct_answers=[
            answer for answer in correct_answers if answer.id in [user_answer.answer_id for user_answer in user_answers]])
        try:
            db.add(stats)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400, detail="Ошибка сохранения статистики")
    return {"status": "success"}


@app.get('/article', response_model=List[ArticleResponse])
def get_articles(db: Session = Depends(get_db)):
    articles = db.query(Article).filter(
        Article.status == ArticleStatus.PUBLISHED).all()
    return articles


@app.post('/article', response_model=ArticleResponse)
def create_article(article: ArticleCreateBody, db: Session = Depends(get_db)):
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


@app.post('/upload', response_model=MediaResponse)
def upload_file(name: str | None = None, file: UploadFile = File(...)):
    file_url = s3_service.upload_file(file.file, name or file.filename)

    if not file_url:
        raise HTTPException(
            status_code=400, detail="Ошибка при загрузке файла")

    return {"url": file_url}
