from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

from pymongo.errors import PyMongoError

from .exceptions import (
    TaskNotFoundError,
    TaskPersistenceError,
    TaskValidationError,
)
from .models import PriorityLevel, Status, Task
from .services import TaskService


@dataclass
class TaskManager:
    
    _service: TaskService

    def create_task(
        self,
        *,
        title: str,
        description: str = "",
        due_date: Optional[datetime] = None,
        priority_level: PriorityLevel = PriorityLevel.MEDIUM,
    ) -> Task:
        """Create and persist a new Task or raise TaskValidationError.
        
        Raises:
            TaskValidationError: if the task data is invalid.
            TaskPersistenceError: if persisting the task fails.
        """
        try:
            task = Task(
                title=title,
                description=description,
                due_date=due_date,
                priority_level=priority_level,
            )
        except TaskValidationError:
            # Let the callers handle validation issues explicitly
            raise

        try:
            return self._service.create_task(task)
        except PyMongoError as exc:  # pragma: no cover - defensive
            raise TaskPersistenceError(f"Failed to create task: {exc}") from exc

    def create_tasks_bulk(
        self,
        tasks_data: Iterable[dict],
    ) -> List[Task]:
        """
        Create and persist multiple tasks in a single bulk operation.

        Raises:
            TaskValidationError: if any task data is invalid.
            TaskPersistenceError: if persisting the tasks fails.
        """
        tasks: List[Task] = []

        try:
            for data in tasks_data:
                title = (data.get("title") or "").strip()
                if not title:
                    raise TaskValidationError("Task title cannot be empty.")

                task = Task(
                    title=title,
                    description=data.get("description", ""),
                    due_date=data.get("due_date"),
                    priority_level=data.get("priority_level", PriorityLevel.MEDIUM),
                )
                tasks.append(task)
        except TaskValidationError:
            # Let the callers handle validation issues explicitly
            raise
        except Exception as exc:
            raise TaskValidationError(f"Invalid bulk task payload: {exc}") from exc

        try:
            return self._service.create_tasks_bulk(tasks)
        except PyMongoError as exc:
            raise TaskPersistenceError(f"Failed to bulk-create tasks: {exc}") from exc

    def get_task(self, task_id: str) -> Task:
        """Return a single task or raise TaskNotFoundError.
        
        Raises:
            TaskNotFoundError: if the task does not exist.
            TaskPersistenceError: if fetching the task fails.
        """
        try:
            task = self._service.get_task(task_id)
        except PyMongoError as exc:  # pragma: no cover - defensive
            raise TaskPersistenceError(f"Failed to fetch task {task_id!r}: {exc}") from exc

        if task is None:
            raise TaskNotFoundError(f"Task {task_id!r} not found.")
        return task

    def list_tasks(
        self,
        *,
        status: Optional[Status] = None,
        priority: Optional[PriorityLevel] = None,
        due_date: Optional[datetime] = None,
    ) -> List[Task]:
        """Return tasks, optionally filtered by status, priority, or due date.
        
        Raises:
            TaskPersistenceError: if listing the tasks fails.
        """
        try:
            return self._service.list_tasks(
                status=status,
                priority=priority,
                due_date=due_date,
            )
        except PyMongoError as exc:  # pragma: no cover - defensive
            raise TaskPersistenceError(f"Failed to list tasks: {exc}") from exc

    def update_task(
        self,
        task_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority_level: Optional[PriorityLevel] = None,
        status: Optional[Status] = None,
    ) -> Task:
        """
        Update an existing task and return the updated object.

        Raises:
            TaskNotFoundError: if the task does not exist.
            TaskValidationError: if the new values are invalid.
            TaskPersistenceError: if persisting the update fails.
        """

        task = self._service.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id!r} not found.")

        try:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if due_date is not None:
                task.due_date = due_date
            if priority_level is not None:
                task.priority_level = priority_level
            if status is not None:
                task.status = status
        except TaskValidationError:
            raise

        try:
            updated = self._service.update_task(
                task_id,
                title=title,
                description=description,
                due_date=due_date,
                priority_level=priority_level,
                status=status,
            )
        except PyMongoError as exc:
            raise TaskPersistenceError(f"Failed to update task {task_id!r}: {exc}") from exc

        if updated is None:
            raise TaskNotFoundError(f"Task {task_id!r} no longer exists.")

        return updated

    def complete_task(self, task_id: str) -> Task:
        """
        Mark a task as completed and persist the change.
        
        Raises:
            TaskNotFoundError: if the task does not exist.
            TaskPersistenceError: if marking the task as completed fails.
        """
        try:
            updated = self._service.update_task(task_id, status=Status.COMPLETED)
        except PyMongoError as exc:
            raise TaskPersistenceError(
                f"Failed to mark task {task_id!r} as completed: {exc}"
            ) from exc

        if updated is None:
            raise TaskNotFoundError(f"Task {task_id!r} no longer exists.")

        return updated

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task.

        Raises:
            TaskNotFoundError: if the task does not exist.
            TaskPersistenceError: if deletion fails unexpectedly.
        """
        try:
            deleted = self._service.delete_task(task_id)
        except PyMongoError as exc:
            raise TaskPersistenceError(f"Failed to delete task {task_id!r}: {exc}") from exc

        if not deleted:
            raise TaskNotFoundError(f"Task {task_id!r} not found.")


