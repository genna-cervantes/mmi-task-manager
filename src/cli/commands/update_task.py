from __future__ import annotations

import argparse
import sys
from typing import Optional

from ...core.task.exceptions import TaskNotFoundError, TaskPersistenceError, TaskValidationError
from ...core.task.manager import TaskManager
from ...core.task.models import PriorityLevel, Status
from ...core.task.services import TaskService
from ...db.base import get_tasks_collection
from ...utils.utils import DATE_FORMAT, parse_due_date
from ..style import print_error, print_success


def _handle_update_task(args: argparse.Namespace) -> int:
    task_id = getattr(args, "id", None)
    if not task_id:
        print_error("Task id is required.")
        return 1

    title: Optional[str] = args.title
    description: Optional[str] = args.description

    due_date = None
    if getattr(args, "due_date", None):
        due_date = parse_due_date(args.due_date)
        if due_date is None:
            print_error(
                f"Invalid date format: {args.due_date!r}. Expected {DATE_FORMAT}."
            )
            return 1

    priority_level = None
    if getattr(args, "priority", None):
        try:
            priority_level = PriorityLevel(args.priority)
        except ValueError:
            print_error(
                f"Invalid priority level: {args.priority!r}. "
                f"Valid values are: {[p.value for p in PriorityLevel]}"
            )
            return 1

    status = None
    if getattr(args, "status", None):
        try:
            status = Status(args.status)
        except ValueError:
            print_error(
                f"Invalid status: {args.status!r}. "
                f"Valid values are: {[s.value for s in Status]}"
            )
            return 1

    manager = TaskManager(TaskService(get_tasks_collection()))
    try:
        updated = manager.update_task(
            task_id,
            title=title,
            description=description,
            due_date=due_date,
            priority_level=priority_level,
            status=status,
        )
    except TaskNotFoundError:
        print_error(f"Task {task_id} not found.")
        return 1
    except TaskValidationError as exc:
        print_error(f"Invalid update: {exc}")
        return 1
    except TaskPersistenceError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Updated task {updated.id}: {updated.title}")
    return 0


def register_update_task_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    parser = subparsers.add_parser(
        "update",
        help="Update an existing task",
        description="Update title, description, due date, priority, or status of a task.",
    )

    parser.add_argument(
        "id",
        help="Identifier of the task to update.",
    )

    parser.add_argument(
        "--title",
        help="New title for the task.",
    )

    parser.add_argument(
        "-d",
        "--description",
        help="New description for the task.",
    )

    parser.add_argument(
        "--due-date",
        metavar="YYYY-MM-DD",
        help="New due date for the task.",
    )

    parser.add_argument(
        "-p",
        "--priority",
        choices=[p.value for p in PriorityLevel],
        help="New priority level for the task.",
    )

    parser.add_argument(
        "--status",
        choices=[s.value for s in Status],
        help="New status for the task.",
    )

    parser.set_defaults(func=_handle_update_task)



