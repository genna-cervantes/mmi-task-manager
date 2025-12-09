from __future__ import annotations

import argparse

from ...core.task.exceptions import TaskNotFoundError, TaskPersistenceError
from ...core.task.manager import TaskManager
from ...core.task.services import TaskService
from ...db.base import get_tasks_collection
from ..style import print_error, print_success


def _handle_complete_task(args: argparse.Namespace) -> int:
    task_id = getattr(args, "id", None)
    if not task_id:
        print_error("Task id is required.")
        return 1

    manager = TaskManager(TaskService(get_tasks_collection()))
    try:
        updated = manager.complete_task(task_id)
    except TaskNotFoundError:
        print_error(f"Task {task_id} not found.")
        return 1
    except TaskPersistenceError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Marked task {updated.id} as completed.")
    return 0


def register_complete_task_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    parser = subparsers.add_parser(
        "complete",
        help="Mark a task as completed",
        description="Mark an existing task as completed.",
    )

    parser.add_argument(
        "id",
        help="Identifier of the task to mark as completed.",
    )

    parser.set_defaults(func=_handle_complete_task)



