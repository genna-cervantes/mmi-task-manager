from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core.task.exceptions import TaskPersistenceError, TaskValidationError
from ...core.task.manager import TaskManager
from ...core.task.models import PriorityLevel
from ...core.task.services import TaskService
from ...db.base import get_tasks_collection
from ...utils.utils import DATE_FORMAT, parse_due_date
from ..style import print_error, print_success


def _load_tasks_from_file(path: str) -> List[Dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {file_path}: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("Bulk file must contain a JSON array of task objects.")

    return data


def _normalise_task_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw JSON task payload into a structure suitable for TaskManager.
    """
    title = (str(raw.get("title", "")).strip())
    description = str(raw.get("description", "") or "").strip()

    raw_due_date: Optional[str] = raw.get("due_date")
    due_date = parse_due_date(raw_due_date) if raw_due_date else None
    if raw_due_date and due_date is None:
        raise TaskValidationError(
            f"Invalid date format: {raw_due_date!r}. Expected {DATE_FORMAT}."
        )

    priority_str = raw.get("priority", PriorityLevel.MEDIUM.value)
    try:
        priority_level = PriorityLevel(priority_str)
    except ValueError:
        raise TaskValidationError(
            f"Invalid priority level: {priority_str!r}. "
            f"Valid values are: {[p.value for p in PriorityLevel]}"
        )

    return {
        "title": title,
        "description": description,
        "due_date": due_date,
        "priority_level": priority_level,
    }


def _handle_add_tasks_bulk(args: argparse.Namespace) -> int:
    path = getattr(args, "file", None)
    if not path:
        print_error("Path to JSON file is required.")
        return 1

    try:
        raw_tasks = _load_tasks_from_file(path)
    except (FileNotFoundError, ValueError) as exc:
        print_error(str(exc))
        return 1

    payloads: List[Dict[str, Any]] = []
    try:
        for raw in raw_tasks:
            if not isinstance(raw, dict):
                raise TaskValidationError("Each item in bulk file must be an object.")
            payloads.append(_normalise_task_payload(raw))
    except TaskValidationError as exc:
        print_error(f"Invalid bulk task data: {exc}")
        return 1

    manager = TaskManager(TaskService(get_tasks_collection()))
    try:
        created_tasks = manager.create_tasks_bulk(payloads)
    except TaskValidationError as exc:
        print_error(f"Invalid bulk task data: {exc}")
        return 1
    except TaskPersistenceError as exc:
        print_error(str(exc))
        return 1

    count = len(created_tasks)
    if count == 0:
        print_success("No tasks created (input file was empty).")
    else:
        print_success(f"Created {count} tasks in bulk.")
    return 0


def register_add_tasks_bulk_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    parser = subparsers.add_parser(
        "add-bulk",
        help="Bulk-create tasks from a JSON file",
        description=(
            "Create multiple tasks in one go from a JSON file containing an array "
            "of task objects (with fields: title, description, due_date, priority)."
        ),
    )

    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to a JSON file with an array of task definitions.",
    )

    parser.set_defaults(func=_handle_add_tasks_bulk)


