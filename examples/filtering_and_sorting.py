#!/usr/bin/env python3
"""Shows task filtering and sorting methods."""

from datetime import datetime, timedelta
from src.task_manager import TaskManager


def main():
    """Demo filtering and sorting tasks."""
    # Create a new task manager
    manager = TaskManager()
    
    # Set up dates for testing
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    next_week = (datetime.now() + timedelta(days=7)).date().isoformat()
    
    # Add sample tasks
    manager.add_task(
        title="Overdue high priority",
        description="This task is overdue with high priority",
        due_date=yesterday,
        priority="high",
        category="Work"
    )
    
    manager.add_task(
        title="Due today medium priority",
        description="This task is due today with medium priority",
        due_date=today,
        priority="medium",
        category="Personal"
    )
    
    manager.add_task(
        title="Due tomorrow low priority",
        description="This task is due tomorrow with low priority",
        due_date=tomorrow,
        priority="low",
        category="Work"
    )
    
    manager.add_task(
        title="Due next week high priority",
        description="This task is due next week with high priority",
        due_date=next_week,
        priority="high",
        category="Personal"
    )
    
    task5 = manager.add_task(
        title="Completed task",
        description="This task is already completed",
        due_date=yesterday,
        priority="medium",
        category="Work"
    )
    
    # Mark one task as completed
    manager.mark_task_completed(task5.task_id)
    
    # Print all tasks
    print("All tasks:")
    for task in manager.get_all_tasks():
        print(f"- {task}")
    
    # Filter by status
    print("\nPending tasks:")
    for task in manager.get_pending_tasks():
        print(f"- {task}")
    
    print("\nCompleted tasks:")
    for task in manager.get_completed_tasks():
        print(f"- {task}")
    
    # Filter by priority
    print("\nHigh priority tasks:")
    for task in manager.get_tasks_by_priority("high"):
        print(f"- {task}")
    
    print("\nMedium priority tasks:")
    for task in manager.get_tasks_by_priority("medium"):
        print(f"- {task}")
    
    print("\nLow priority tasks:")
    for task in manager.get_tasks_by_priority("low"):
        print(f"- {task}")
    
    # Filter by category
    print("\nWork category tasks:")
    for task in manager.get_tasks_by_category("Work"):
        print(f"- {task}")
    
    print("\nPersonal category tasks:")
    for task in manager.get_tasks_by_category("Personal"):
        print(f"- {task}")
    
    # Filter by due date
    print("\nTasks due today:")
    for task in manager.get_tasks_by_due_date(today):
        print(f"- {task}")
    
    print("\nTasks due before tomorrow:")
    for task in manager.get_tasks_due_before(tomorrow):
        print(f"- {task}")
    
    print("\nTasks due after today:")
    for task in manager.get_tasks_due_after(today):
        print(f"- {task}")
    
    # Get overdue tasks
    print("\nOverdue tasks:")
    for task in manager.get_overdue_tasks():
        print(f"- {task}")
    
    # Sort tasks
    print("\nTasks sorted by due date:")
    for task in manager.sort_tasks("due_date"):
        print(f"- {task.due_date}: {task.title}")
    
    print("\nTasks sorted by priority:")
    for task in manager.sort_tasks("priority"):
        print(f"- {task.priority.name}: {task.title}")
    
    print("\nTasks sorted by title:")
    for task in manager.sort_tasks("title"):
        print(f"- {task.title}")
    
    # Custom filtering
    print("\nHigh priority work tasks:")
    work_high = manager.filter_tasks(
        lambda t: t.category.lower() == "work" and t.priority.name.lower() == "high"
    )
    for task in work_high:
        print(f"- {task}")
    
    # Search tasks
    print("\nTasks containing 'priority':")
    for task in manager.search_tasks("priority"):
        print(f"- {task}")


if __name__ == "__main__":
    main()