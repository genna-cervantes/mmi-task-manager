from __future__ import annotations

import os
import sys
from typing import Iterable

from ..core.task.models import PriorityLevel, Status, Task
from ..utils.utils import DATE_FORMAT

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

FG_GREEN = "\033[32m"
FG_RED = "\033[31m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_GRAY = "\033[90m"

def _supports_color() -> bool:
    """Return True if the current stdout should use colors."""
    if os.environ.get("MMI_NO_COLOR"):
        return False
    return sys.stdout.isatty()

USE_COLOR = _supports_color()

def _wrap(text: str, *codes: str) -> str:
    if not USE_COLOR or not codes:
        return text
    return "".join(codes) + text + RESET

def style_ok(text: str) -> str:
    return _wrap(text, FG_GREEN, BOLD)


def style_error(text: str) -> str:
    return _wrap(text, FG_RED, BOLD)


def style_muted(text: str) -> str:
    return _wrap(text, FG_GRAY)


def print_success(message: str) -> None:
    print(f"{style_ok('✔')} {message}")


def print_error(message: str) -> None:
    print(f"{style_error('✖')} {message}", file=sys.stderr)

def format_status_badge(status: Status) -> str:
    icon = {
        Status.PENDING: "●",
        Status.IN_PROGRESS: "◔",
        Status.COMPLETED: "✔",
    }.get(status, "●")

    if status is Status.COMPLETED:
        return _wrap(f"{icon} {status.value}", FG_GREEN)
    if status is Status.IN_PROGRESS:
        return _wrap(f"{icon} {status.value}", FG_BLUE)
    return _wrap(f"{icon} {status.value}", FG_YELLOW)

def format_priority_badge(priority: PriorityLevel) -> str:
    icon = {
        PriorityLevel.LOW: "↓",
        PriorityLevel.MEDIUM: "→",
        PriorityLevel.HIGH: "↑",
    }.get(priority, "→")

    if priority is PriorityLevel.HIGH:
        return _wrap(f"{icon} {priority.value}", FG_RED, BOLD)
    if priority is PriorityLevel.LOW:
        return _wrap(f"{icon} {priority.value}", FG_GRAY)
    return _wrap(f"{icon} {priority.value}", FG_CYAN)

def format_due_date(due_date) -> str:
    from datetime import datetime

    if due_date is None:
        return style_muted("None")

    if not isinstance(due_date, datetime):
        return str(due_date)

    today = datetime.utcnow().date()
    date_str = due_date.strftime(DATE_FORMAT)

    if due_date.date() < today:
        return _wrap(date_str, FG_RED)
    if due_date.date() == today:
        return _wrap(date_str, FG_YELLOW, BOLD)
    return _wrap(date_str, FG_GREEN)

def print_tasks_table(tasks: Iterable[Task]) -> None:
    """Pretty-print tasks in a compact table."""
    tasks_list = list(tasks)
    if not tasks_list:
        print(style_muted("No tasks found."))
        return

    headers = ["ID", "Status", "Priority", "Due", "Title", "Description"]
    rows = []
    for t in tasks_list:
        status = format_status_badge(t.status)
        priority = format_priority_badge(t.priority_level)
        due = format_due_date(t.due_date)
        description = (t.description or "").strip() or style_muted("None")
        rows.append([t.id, status, priority, due, t.title, description])

    def visible_length(s: str) -> int:
        import re
        return len(re.sub(r"\x1b\[[0-9;]*m", "", s))

    col_count = len(headers)
    widths = [0] * col_count
    for idx, header in enumerate(headers):
        widths[idx] = max(widths[idx], len(header))

    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], visible_length(str(cell)))

    header_label = " / ".join(headers)
    print(style_muted(header_label))

    def pad(cell: str, width: int) -> str:
        pad_len = width - visible_length(cell)
        return cell + " " * max(pad_len, 0)

    for row in rows:
        print("  ".join(pad(str(row[i]), widths[i]) for i in range(col_count)))


