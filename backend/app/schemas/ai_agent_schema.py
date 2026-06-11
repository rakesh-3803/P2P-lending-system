from pydantic import BaseModel


class AIQuestion(BaseModel):
    question: str