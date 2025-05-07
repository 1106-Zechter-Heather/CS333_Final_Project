# Task Manager

A Python task management system for tracking and organizing tasks.

## Features

- Create, update, and delete tasks
- Assign priorities and deadlines
- Filter and sort by multiple criteria
- Track task completion status
- Import/export CSV and JSON

## Installation

```bash
pip install task-manager  # From PyPI
# or
git clone https://github.com/yourusername/task_manager.git
cd task_manager
pip install -e .  # From source
```

## CLI Usage

```bash
# Add a task
taskman add "Complete documentation" --priority high --due 2023-12-31 --category Work

# List tasks
taskman list
taskman list --pending
taskman list --overdue

# Manage tasks
taskman show <task-id>
taskman update <task-id> --title "New title" --priority medium
taskman complete <task-id>
taskman delete <task-id>

# Import/Export
taskman export tasks.csv
taskman import tasks.csv

# Statistics
taskman stats
```

## Python API

```python
from task_manager import TaskManager

# Initialize
manager = TaskManager()

# Add tasks
task = manager.add_task(
    title="Complete project",
    due_date="2023-12-31",
    priority="high",
    category="Work"
)

# Filter tasks
work_tasks = manager.get_tasks_by_category("Work")
high_priority = manager.get_tasks_by_priority("high")
overdue = manager.get_overdue_tasks()

# Update status
manager.mark_task_completed(task.task_id)

# Save/load
manager.save_to_file("tasks.json")
manager.export_to_csv("tasks.csv")
```

## Development

```bash
# Setup
pip install -r dev-requirements.txt
pre-commit install

# Common commands
make test        # Run tests
make coverage    # Generate coverage report
make lint        # Run style checks
make type-check  # Run type checks
make format      # Format code
make build       # Build package
```