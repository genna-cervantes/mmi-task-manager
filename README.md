## CLI Task Manager (`mmi`)

`mmi` is a small, MongoDB‑backed CLI task manager for creating, listing, updating, completing, and deleting tasks from your terminal.

---

## Requirements

- **Python**: >= **3.12**
- **MongoDB**: running locally or reachable via connection string  
  - Default URI: `mongodb://localhost:27017`  
  - Default database name: `task_manager`
- **Python dependencies**:
  - `pymongo` (installed automatically if you install the project as a package, or manually via `pip install pymongo`)

---

## Setup

All commands below assume you are in the project root (`mmi`).

1. **Create and activate a virtual environment (recommended)**

   ```powershell
   # From the project root
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install dependencies**

   Using the provided `pyproject.toml`, the simplest approach is to install the project in editable mode:

   ```powershell
   pip install --upgrade pip
   pip install -e .
   ```

   If you prefer, you can also install just the runtime dependency directly:

   ```powershell
   pip install pymongo
   ```

3. **Ensure MongoDB is running**

   - Start a local MongoDB instance (default port 27017), **or**
   - Point the app to a remote MongoDB instance via environment variables (see below).

---

## Configuration (MongoDB)

You can override the default connection settings using environment variables:

- **`MONGO_URI`**: MongoDB connection URI  
  - Defaults to `mongodb://localhost:27017`
- **`DB_NAME`**: Database name  
  - Defaults to `task_manager`

Example (PowerShell):

```powershell
$env:MONGO_URI = "mongodb://localhost:27017"
$env:DB_NAME = "mmi_tasks"
```

---

## Running the CLI

From the project root, with your virtual environment activated and MongoDB running:

### General help

```powershell
python -m src.cli.main --help
```

### List available commands

```powershell
python -m src.cli.main --help
```

The help output will show subcommands such as `add`, `add-bulk`, `list`, `update`, `complete`, and `delete`.

### Examples

- **Add a new task**

  ```powershell
  python -m src.cli.main add "Buy groceries" `
      -d "Milk, eggs, bread" `
      --due-date 2025-12-10 `
      --priority high
  ```

- **List tasks**

  ```powershell
  python -m src.cli.main list
  ```

- **Mark a task as complete**

  ```powershell
  python -m src.cli.main complete <task_id>
  ```

Replace `<task_id>` with the actual ID shown in the `list` output.

---

## Development Notes

- The main entrypoint is `src/cli/main.py` (invoked as `python -m src.cli.main`).
- MongoDB collections and indices are configured in `src/db/base.py`.


