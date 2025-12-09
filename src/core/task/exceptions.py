class TaskManagerError(Exception):
    """Base exception for the task manager."""


class TaskNotFoundError(TaskManagerError):
    """Raised when a task with the given identifier cannot be found."""


class TaskValidationError(TaskManagerError):
    """Raised when task data is invalid or incomplete."""


class TaskPersistenceError(TaskManagerError):
    """Raised when a task cannot be saved, updated, or deleted in storage."""