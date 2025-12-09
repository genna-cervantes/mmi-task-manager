from __future__ import annotations

import argparse
from datetime import datetime
from typing import Optional

from ...core.task.exceptions import TaskPersistenceError
from ...core.task.manager import TaskManager
from ...core.task.models import PriorityLevel, Status
from ...core.task.services import TaskService
from ...db.base import get_tasks_collection
from ...utils.utils import DATE_FORMAT, parse_due_date
from ..style import print_error, print_tasks_table


def _handle_list_tasks(args: argparse.Namespace) -> int:
    status: Optional[Status] = None
    if getattr(args, "status", None):
        status = Status(args.status)

    priority: Optional[PriorityLevel] = None
    if getattr(args, "priority", None):
        priority = PriorityLevel(args.priority)

    due_date: Optional[datetime] = None
    if getattr(args, "due_date", None):
        due_date = parse_due_date(args.due_date)
        if due_date is None:
            print_error(
                f"Invalid date format: {args.due_date!r}. Expected {DATE_FORMAT}."
            )
            return 1

    manager = TaskManager(TaskService(get_tasks_collection()))
    try:
        tasks = manager.list_tasks(status=status, priority=priority, due_date=due_date)
    except TaskPersistenceError as exc:
        print_error(str(exc))
        return 1

    print_tasks_table(tasks)
    return 0


def register_list_tasks_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    parser = subparsers.add_parser(
        "list",
        help="List tasks",
        description="List tasks, optionally filtered by status, priority, or due date.",
    )

    parser.add_argument(
        "--status",
        choices=[s.value for s in Status],
        help="Filter tasks by status.",
    )

    parser.add_argument(
        "--priority",
        choices=[p.value for p in PriorityLevel],
        help="Filter tasks by priority level.",
    )

    parser.add_argument(
        "--due-date",
        metavar="YYYY-MM-DD",
        help="Filter tasks by exact due date.",
    )

    parser.set_defaults(func=_handle_list_tasks)