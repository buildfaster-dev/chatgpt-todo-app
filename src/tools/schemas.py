from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# --- Error Handling ---


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ToolError(BaseModel):
    code: ErrorCode
    message: str
    details: dict | None = None


# --- Task Models ---


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)


class TaskCreate(TaskBase):
    parent_id: int | None = Field(None, ge=1)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        return v.strip()


class Task(TaskBase):
    id: int
    completed: bool = False
    created_at: datetime
    parent_id: int | None = None
    subtasks: list[Task] = []

    model_config = {"from_attributes": True}


# --- Tool Input Schemas ---


class AddTaskInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="The task description")
    parent_id: int | None = Field(None, ge=1, description="Optional parent task ID for creating subtasks")

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        return v.strip()


class ListTasksInput(BaseModel):
    filter: str = Field("all", description="Filter tasks by completion status")
    parent_id: int | None = Field(None, ge=1, description="Filter to subtasks of a specific parent")

    @field_validator("filter")
    @classmethod
    def validate_filter(cls, v: str) -> str:
        if v not in ("all", "complete", "incomplete"):
            raise ValueError("filter must be 'all', 'complete', or 'incomplete'")
        return v


class CompleteTaskInput(BaseModel):
    task_id: int = Field(..., ge=1, description="The ID of the task to complete")


class DeleteTaskInput(BaseModel):
    task_id: int = Field(..., ge=1, description="The ID of the task to delete")


class DecomposeTaskInput(BaseModel):
    task_id: int = Field(..., ge=1, description="The ID of the task to decompose")
    subtask_titles: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Titles for the subtasks to create",
    )

    @field_validator("subtask_titles")
    @classmethod
    def validate_subtask_titles(cls, v: list[str]) -> list[str]:
        return [title.strip() for title in v if title.strip()]
