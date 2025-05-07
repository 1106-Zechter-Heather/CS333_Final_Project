#!/usr/bin/env python3
"""
Task statistics example for Task Manager.

This example demonstrates how to generate and analyze statistics
about tasks, including completion rates, category breakdowns,
and priority distributions.
"""

from datetime import datetime, timedelta
from src.task_manager import TaskManager


def main():
    """Run the task statistics example."""
    # Create a new task manager
    manager = TaskManager()
    
    # Set up dates for testing
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    
    # Add tasks with various attributes
    # Overdue task
    task1 = manager.add_task(
        title="Overdue Task",
        description="This task is overdue",
        due_date=yesterday,
        priority="high",
        category="Work"
    )
    
    # Pending tasks
    manager.add_task(
        title="Today's Task",
        description="This task is due today",
        due_date=today,
        priority="medium",
        category="Home"
    )
    
    manager.add_task(
        title="Tomorrow's Task",
        description="This task is due tomorrow",
        due_date=tomorrow,
        priority="low",
        category="Work"
    )
    
    # Add more tasks with different categories
    manager.add_task(
        title="Personal Task 1",
        description="Description for personal task",
        due_date=tomorrow,
        priority="medium",
        category="Personal"
    )
    
    manager.add_task(
        title="Personal Task 2",
        description="Another personal task",
        due_date=tomorrow,
        priority="high",
        category="Personal"
    )
    
    # Add tasks and mark as completed/cancelled
    task6 = manager.add_task(
        title="Completed Work Task",
        description="This task is completed",
        due_date=yesterday,
        priority="high",
        category="Work"
    )
    manager.mark_task_completed(task6.task_id)
    
    task7 = manager.add_task(
        title="Completed Personal Task",
        description="This personal task is completed",
        due_date=yesterday,
        priority="low",
        category="Personal"
    )
    manager.mark_task_completed(task7.task_id)
    
    task8 = manager.add_task(
        title="Cancelled Task",
        description="This task is cancelled",
        due_date=tomorrow,
        priority="medium",
        category="Home"
    )
    manager.mark_task_cancelled(task8.task_id)
    
    # Generate statistics
    stats = manager.get_stats()
    
    # Display overall statistics
    print("Task Statistics")
    print("===============")
    print(f"Total tasks: {stats['total']}")
    print(f"Completed: {stats['completed']} ({stats['completion_rate']}%)")
    print(f"Pending: {stats['pending']}")
    print(f"Cancelled: {stats['cancelled']}")
    print(f"Overdue: {stats['overdue']}")
    
    # Display category breakdown
    print("\nCategory Breakdown")
    print("-----------------")
    for category, count in sorted(stats['categories'].items()):
        print(f"{category}: {count} task(s)")
    
    # Display priority breakdown
    print("\nPriority Breakdown")
    print("-----------------")
    print(f"High: {stats['priorities']['high']} task(s)")
    print(f"Medium: {stats['priorities']['medium']} task(s)")
    print(f"Low: {stats['priorities']['low']} task(s)")
    
    # Calculate category completion rates
    print("\nCategory Completion Rates")
    print("------------------------")
    work_tasks = manager.get_tasks_by_category("Work")
    work_completed = [t for t in work_tasks if t.status == TaskStatus.COMPLETED]
    work_rate = len(work_completed) / len(work_tasks) * 100 if work_tasks else 0
    print(f"Work: {work_rate:.1f}% ({len(work_completed)}/{len(work_tasks)})")
    
    personal_tasks = manager.get_tasks_by_category("Personal")
    personal_completed = [t for t in personal_tasks if t.status == TaskStatus.COMPLETED]
    personal_rate = len(personal_completed) / len(personal_tasks) * 100 if personal_tasks else 0
    print(f"Personal: {personal_rate:.1f}% ({len(personal_completed)}/{len(personal_tasks)})")
    
    home_tasks = manager.get_tasks_by_category("Home")
    home_completed = [t for t in home_tasks if t.status == TaskStatus.COMPLETED]
    home_rate = len(home_completed) / len(home_tasks) * 100 if home_tasks else 0
    print(f"Home: {home_rate:.1f}% ({len(home_completed)}/{len(home_tasks)})")
    
    # Generate task urgency report
    print("\nTask Urgency Report")
    print("------------------")
    overdue_tasks = manager.get_overdue_tasks()
    today_tasks = manager.get_tasks_by_due_date(today)
    tomorrow_tasks = manager.get_tasks_by_due_date(tomorrow)
    future_tasks = manager.get_tasks_due_after(tomorrow)
    
    print(f"Overdue: {len(overdue_tasks)} task(s)")
    print(f"Due today: {len(today_tasks)} task(s)")
    print(f"Due tomorrow: {len(tomorrow_tasks)} task(s)")
    print(f"Due later: {len(future_tasks)} task(s)")


if __name__ == "__main__":
    # Need to import TaskStatus here to avoid circular import in the example
    from src.task import TaskStatus
    main()