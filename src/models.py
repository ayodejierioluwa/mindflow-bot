from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    TASK = "task"
    EXPENSE = "expense"
    NOTE = "note"
    READ_LATER = "read_later"
    SET_PERSONA = "set_persona"

class PersonaItem(BaseModel):
    name: str = Field(description="The desired new name the user wants to call their assistant, e.g. Jarvis, Friday, Nova, Alfred")


class TaskItem(BaseModel):
    title: str = Field(description="Clear, actionable task title")
    due_date: Optional[str] = Field(None, description="Due date or time mention, e.g. 'Tomorrow 3pm', 'Friday'")
    priority: str = Field("medium", description="Priority level: low, medium, or high")
    category: str = Field("Personal", description="Category e.g. Work, Personal, Fitness, Admin")

class ExpenseItem(BaseModel):
    merchant: str = Field(description="Name of the vendor, store, or recipient")
    amount: float = Field(description="Numerical amount of the expense")
    currency: str = Field("USD", description="Currency symbol or 3-letter code, e.g. USD, EUR, GBP, NGN")
    category: str = Field("General", description="Category e.g. Food & Dining, Travel, Software, Utilities")
    date: Optional[str] = Field(None, description="Date of the expense if stated")

class NoteItem(BaseModel):
    title: str = Field(description="Short summary title of the idea or note")
    summary: str = Field(description="Bullet-point summary or key takeaways")
    tags: List[str] = Field(default_factory=list, description="Relevant contextual tags")

class ParsedCapture(BaseModel):
    intent: IntentType = Field(description="Primary category of the captured input or 'task' if mixed")
    summary_message: str = Field(description="A user-friendly, friendly confirmation line suitable for Telegram")
    tasks: List[TaskItem] = Field(default_factory=list, description="List of actionable tasks detected")
    expenses: List[ExpenseItem] = Field(default_factory=list, description="List of financial expenses detected")
    note: Optional[NoteItem] = None
    persona: Optional[PersonaItem] = None
    
    # Backwards compatibility helpers
    @property
    def task(self) -> Optional[TaskItem]:
        return self.tasks[0] if self.tasks else None

    @property
    def expense(self) -> Optional[ExpenseItem]:
        return self.expenses[0] if self.expenses else None
