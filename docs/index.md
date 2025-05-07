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
git clone https://github.com/1106-Zechter-Heather/CS333_Final_Project.git
cd task_manager
pip install -e .  # From source
```

## Usage

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

# Save/load
manager.save_to_file("tasks.json")
```

## CLI Commands

```bash
# Add a task
taskman add "Complete documentation" --priority high --due 2023-12-31

# List tasks
taskman list
taskman list --pending
taskman list --overdue

# Show task details
taskman show <task-id>

# Update task
taskman update <task-id> --title "New title" --priority medium

# Mark as complete
taskman complete <task-id>
```

## Code Examples

Check out the examples directory for more detailed usage examples.

## Test Coverage

- 96% unit test coverage
- 7+ integration tests
- Automated testing via GitHub Actions
- Automated deployment to PyPI