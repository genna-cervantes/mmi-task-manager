from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .commands.add_task import register_add_task_command
from .commands.add_tasks_bulk import register_add_tasks_bulk_command
from .commands.list_tasks import register_list_tasks_command
from .commands.update_task import register_update_task_command
from .commands.complete_task import register_complete_task_command
from .commands.delete_task import register_delete_task_command


def build_parser() -> argparse.ArgumentParser:
    """
    Construct the top-level argument parser for the CLI.

    New subcommands should register themselves here via their respective
    `register_*_command` helper functions.
    """
    parser = argparse.ArgumentParser(
        prog="mmi",
        description="CLI Task Manager",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="<command>",
        required=True,
    )

    # Register individual commands
    register_add_task_command(subparsers)
    register_add_tasks_bulk_command(subparsers)
    register_list_tasks_command(subparsers)
    register_update_task_command(subparsers)
    register_complete_task_command(subparsers)
    register_delete_task_command(subparsers)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entrypoint for the CLI.

    This function is designed so it can be called both from the command line
    and programmatically (e.g. tests) by passing an explicit `argv` list.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    command_func = getattr(args, "func", None)
    if command_func is None:
        parser.print_help()
        return 1

    return int(command_func(args)) 


if __name__ == "__main__":
    sys.exit(main())

