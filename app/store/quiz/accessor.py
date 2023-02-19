from typing import Optional

from aiohttp.web_exceptions import HTTPConflict

from app.base.base_accessor import BaseAccessor
from app.quiz.models import Theme, Question, Answer


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        theme = Theme(
            id=self.app.database.next_theme_id,
            title=str(title)
        )
        self.app.database.themes.append(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        for theme in self.app.database.themes:
            if theme.title == title:
                return theme
        return None

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        for theme in self.app.database.themes:
            if theme.id == id_:
                return theme
        return None

    async def list_themes(self) -> list[Theme]:
        return self.app.database.themes

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        for question in self.app.database.questions:
            if question.title == title:
                return question
        return None

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        question = Question(
            id=self.app.database.next_question_id,
            title=title,
            theme_id=theme_id,
            answers=answers
        )
        self.app.database.questions.append(question)
        return question

    async def list_questions(self) -> list[Question]:
        return self.app.database.questions

    async def list_questions_by_theme_id(self, theme_id: Optional[int] = None) -> list[Question]:
        questions = [question for question in self.app.database.questions if question.theme_id == int(theme_id)]
        return questions

