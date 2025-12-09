from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from pymongo import ReturnDocument
from pymongo.collection import Collection

from .models import PriorityLevel, Status, Task

class TaskService:
    """
    Service layer for working with Task objects.

    This class assumes you pass in a configured MongoDB collection
    """

    def __init__(self, collection: Collection):
        self._collection = collection

    # Helpers
    @staticmethod
    def _serialize(task: Task) -> dict:
        """Convert a Task instance into a MongoDB document."""
        return {
            "_id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority_level": task.priority_level.value,
            "status": task.status.value,
            "created_at": task.created_at,
        }

    @staticmethod
    def _deserialize(doc: dict) -> Task:
        """Convert a MongoDB document into a Task instance."""
        return Task(
            id=str(doc["_id"]),
            title=doc["title"],
            description=doc.get("description", ""),
            due_date=doc.get("due_date"),
            priority_level=PriorityLevel(doc.get("priority_level", PriorityLevel.MEDIUM.value)),
            status=Status(doc.get("status", Status.PENDING.value)),
            created_at=doc.get("created_at", datetime.utcnow()),
        )

    # CRUD
    def create_task(self, task: Task) -> Task:
        """Insert a new Task into the collection."""
        self._collection.insert_one(self._serialize(task))
        return task

    def create_tasks_bulk(self, tasks: Iterable[Task]) -> List[Task]:
        """
        Insert multiple Task instances in a single bulk operation.

        This is more efficient than calling `create_task` repeatedly and is
        suitable for concurrent-style, bulk-creation workflows.
        """
        task_list = list(tasks)
        if not task_list:
            return []

        docs = [self._serialize(task) for task in task_list]
        self._collection.insert_many(docs, ordered=False)
        return task_list

    def get_task(self, task_id: str) -> Optional[Task]:
        """Fetch a single Task by its id."""
        doc = self._collection.find_one({"_id": task_id})
        return self._deserialize(doc) if doc else None

    def list_tasks(
        self,
        status: Optional[Status] = None,
        priority: Optional[PriorityLevel] = None,
        due_date: Optional[datetime] = None,
    ) -> List[Task]:
        """Return all tasks, optionally filtered by status/priority."""
        query: dict = {}
        if status is not None:
            query["status"] = status.value
        if priority is not None:
            query["priority_level"] = priority.value
        if due_date is not None:
            query["due_date"] = due_date

        cursor: Iterable[dict] = self._collection.find(query).sort("created_at", 1)
        return [self._deserialize(doc) for doc in cursor]

    def update_task(
        self,
        task_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority_level: Optional[PriorityLevel] = None,
        status: Optional[Status] = None,
    ) -> Optional[Task]:
        """
        Update fields on a Task and return the updated Task,
        or None if it does not exist.
        """
        updates: dict = {}
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if due_date is not None:
            updates["due_date"] = due_date
        if priority_level is not None:
            updates["priority_level"] = priority_level.value
        if status is not None:
            updates["status"] = status.value

        if not updates:
            return self.get_task(task_id)

        result = self._collection.find_one_and_update(
            {"_id": task_id},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        return self._deserialize(result) if result else None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by id. Returns True if something was deleted."""
        result = self._collection.delete_one({"_id": task_id})
        return result.deleted_count > 0


