from __future__ import annotations

from datetime import datetime
from typing import Optional

DATE_FORMAT = "%Y-%m-%d"

def parse_due_date(raw: str | None) -> datetime | None:
    """
    Parse a raw due-date string into a datetime, or return None.

    This is a shared helper used across CLI commands.
    Callers are responsible for handling a None result if the parse fails.
    """
    if not raw:
        return None

    try:
        return datetime.strptime(raw, DATE_FORMAT)
    except ValueError:
        return None


