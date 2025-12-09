from __future__ import annotations

import argparse
from typing import Optional

from ...core.task.exceptions import TaskPersistenceError, TaskValidationError
from ...core.task.manager import TaskManager
from ...core.task.models import PriorityLevel
from ...core.task.services import TaskService
from ...db.base import get_tasks_collection
from ...utils.utils import DATE_FORMAT, parse_due_date
from ..style import print_error, print_success


def _handle_add_task(args: argparse.Namespace) -> int:
    title: str = (args.title or "").strip()
    if not title:
        print_error("Title is required.")
        return 1

    description: str = (getattr(args, "description", "") or "").strip()

    raw_due_date: Optional[str] = getattr(args, "due_date", None)
    due_date = parse_due_date(raw_due_date)
    if getattr(args, "due_date", None) and due_date is None:
        print_error(f"Invalid date format: {raw_due_date!r}. Expected {DATE_FORMAT}.")
        return 1

    priority_str = getattr(args, "priority", PriorityLevel.MEDIUM.value)
    try:
        priority = PriorityLevel(priority_str)
    except ValueError:
        print_error(
            f"Invalid priority level: {priority_str!r}. "
            f"Valid values are: {[p.value for p in PriorityLevel]}"
        )
        return 1

    manager = TaskManager(TaskService(get_tasks_collection()))
    try:
        created = manager.create_task(
            title=title,
            description=description,
            due_date=due_date,
            priority_level=priority,
        )
    except TaskValidationError as exc:
        print_error(f"Invalid task data: {exc}")
        return 1
    except TaskPersistenceError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Created task {created.id}: {created.title}")
    return 0


def register_add_task_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    parser = subparsers.add_parser(
        "add",
        help="Add a new task",
        description="Create a new task in the task manager.",
    )

    parser.add_argument(
        "title",
        help="Short title for the task.",
    )

    parser.add_argument(
        "-d",
        "--description",
        help="Longer description of the task.",
        default="",
    )

    parser.add_argument(
        "--due-date",
        metavar="YYYY-MM-DD",
        help="Optional due date for the task.",
    )

    parser.add_argument(
        "-p",
        "--priority",
        choices=[p.value for p in PriorityLevel],
        default=PriorityLevel.MEDIUM.value,
        help="Priority level for the task.",
    )

    parser.set_defaults(func=_handle_add_task)


