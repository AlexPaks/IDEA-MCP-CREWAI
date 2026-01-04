from pydantic import BaseModel, Field
from typing import List, Literal

Priority = Literal["P0", "P1", "P2"]

class Issue(BaseModel):
    title: str = Field(min_length=3)
    body: str = Field(min_length=10)
    labels: List[str] = Field(default_factory=list)
    priority: Priority = "P2"
    order: int = Field(ge=1)

class DesignResult(BaseModel):
    design_markdown: str
    issues: List[Issue]
