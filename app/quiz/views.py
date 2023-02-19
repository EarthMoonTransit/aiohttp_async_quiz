from aiohttp_apispec import docs, request_schema, response_schema
from app.quiz.schemes import (
     ThemeListSchema, QuestionSchema, ListQuestionsResponseScheme
)
from app.web.app import View
from app.web.mixins import login_required
from app.web.utils import json_response
from app.quiz.schemes import ThemeSchema
from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    @docs(tags=["Quiz"], summary="Create theme", description="Add new theme to database")
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema, 200)
    @login_required
    async def post(self):
        # TODO: заменить на self.data["title"] после внедрения валидации
        ## TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        data = self.request["data"]
        if await self.store.quizzes.get_theme_by_title(data["title"]):
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=data["title"])
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    @docs(tags=["Quiz"], summary="List themes", description="List users from database")
    @response_schema(ThemeListSchema, 200)
    @login_required
    async def get(self):
        themes = await self.request.app.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme) for theme in themes]
        return json_response(data={"themes": raw_themes})


class QuestionAddView(View):
    @docs(tags=["Quiz"], summary="Create question", description="Add new question to database")
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    @login_required
    async def post(self):
        data = self.request["data"]
        theme = await self.request.app.store.quizzes.get_theme_by_id(data["theme_id"])
        true_answers_counter = 0

        for answer in data["answers"]:
            if answer["is_correct"]:
                true_answers_counter += 1

        if true_answers_counter == 0 or true_answers_counter > 1:
            raise HTTPBadRequest

        if len(data["answers"]) < 2:
            raise HTTPBadRequest

        if theme is None:
            raise HTTPNotFound

        if await self.request.app.store.quizzes.get_question_by_title(data["title"]):
            raise HTTPConflict

        quiz = await self.store.quizzes.create_question(
            title=data["title"],
            theme_id=theme.id,
            answers=data["answers"]
        )
        return json_response(data=QuestionSchema().dump(quiz))


class QuestionListView(View):
    @docs(tags=["Quiz"], summary="List questions", description="List questions from database")
    @response_schema(ListQuestionsResponseScheme, 200)
    @login_required
    async def get(self):
        questions = await self.store.quizzes.list_questions()
        raw_data = [QuestionSchema().dump(question) for question in questions]

        return json_response(data={"questions": raw_data})
