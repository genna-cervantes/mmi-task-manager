from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4
from enum import StrEnum

from .exceptions import TaskValidationError

class PriorityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task:
    """
    Represents a single task in the CLI Task Manager.

    The internal state is encapsulated behind properties so that we can
    validate and constrain changes in one place.
    """

    def __init__(
        self,
        *,
        title: str,
        description: str = "",
        due_date: Optional[datetime] = None,
        priority_level: PriorityLevel = PriorityLevel.MEDIUM,
        status: Status = Status.PENDING,
        created_at: Optional[datetime] = None,
        id: Optional[str] = None,
    ) -> None:
        self._id: str = id or str(uuid4())
        self._title: str = ""
        self._description: str = ""
        self._due_date: Optional[datetime] = None
        self._priority_level: PriorityLevel = PriorityLevel.MEDIUM
        self._status: Status = Status.PENDING
        self._created_at: datetime = created_at or datetime.utcnow()

        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority_level = priority_level
        self.status = status

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        value = (value or "").strip()
        if not value:
            raise TaskValidationError("Task title cannot be empty.")
        self._title = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = (value or "").strip()

    @property
    def due_date(self) -> Optional[datetime]:
        return self._due_date

    @due_date.setter
    def due_date(self, value: Optional[datetime]) -> None:
        self._due_date = value

    @property
    def priority_level(self) -> PriorityLevel:
        return self._priority_level

    @priority_level.setter
    def priority_level(self, value: PriorityLevel) -> None:
        self._priority_level = value

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Status) -> None:
        self._status = value

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def mark_completed(self) -> None:
        """Transition the task to a completed state."""
        self.status = Status.COMPLETED

    def start(self) -> None:
        """Transition the task to in-progress."""
        if self.status == Status.COMPLETED:
            raise TaskValidationError("Cannot start a task that is already completed.")
        self.status = Status.IN_PROGRESS

