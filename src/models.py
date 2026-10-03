from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    TASK = "task"
    EXPENSE = "expense"
    NOTE = "note"
    READ_LATER = "read_later"

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
    intent: IntentType = Field(description="Primary category of the captured input")
    summary_message: str = Field(description="A user-friendly, friendly confirmation line suitable for Telegram")
    task: Optional[TaskItem] = None
    expense: Optional[ExpenseItem] = None
    note: Optional[NoteItem] = None
