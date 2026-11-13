
from pydantic import BaseModel, Field


class StudyAnswer(BaseModel):
    answer: str
    key_points: list[str] = Field(default_factory=list)
    confidence_note: str
