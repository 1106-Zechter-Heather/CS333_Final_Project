#!/usr/bin/env python3
"""
CSV import and export example for Task Manager.

This example demonstrates exporting tasks to CSV format and
importing them back, including handling of special characters
and task attributes.
"""

import os
from src.task_manager import TaskManager


def main():
    """Run the CSV operations example."""
    # Create a new task manager
    manager = TaskManager()
    
    # Add sample tasks with various attributes
    manager.add_task(
        title="Task with special chars: @#$%",
        description="Description with commas, quotes, and \"special\" characters",
        due_date="2023-12-15",
        priority="high",
        category="CSV Test"
    )
    
    # Add a task with a long description
    long_desc = "This is a very long description that spans multiple lines.\n"
    long_desc += "It has line breaks and other formatting that should be preserved.\n"
    long_desc += "The CSV export and import should handle this correctly."
    
    manager.add_task(
        title="Long Description Task",
        description=long_desc,
        due_date="2023-12-20",
        priority="medium",
        category="Long Content"
    )
    
    # Add a task and mark it as completed
    task = manager.add_task(
        title="Completed Task",
        description="This task is already completed",
        due_date="2023-11-01",
        priority="low",
        category="Status Test"
    )
    manager.mark_task_completed(task.task_id)
    
    # Print original tasks
    print("Original tasks:")
    for task in manager.get_all_tasks():
        print(f"- {task}")
        if task.description:
            print(f"  Description: {task.description[:50]}...")
    
    # Export to CSV
    csv_file = "tasks_export.csv"
    print(f"\nExporting tasks to {csv_file}...")
    manager.export_to_csv(csv_file)
    
    # Check the size of the CSV file
    file_size = os.path.getsize(csv_file)
    print(f"CSV file size: {file_size} bytes")
    
    # Create a new manager and import from CSV
    print(f"\nImporting tasks from {csv_file}...")
    new_manager = TaskManager()
    new_manager.import_from_csv(csv_file)
    
    # Print imported tasks
    print("\nImported tasks:")
    for task in new_manager.get_all_tasks():
        print(f"- {task}")
        if task.description:
            print(f"  Description: {task.description[:50]}...")
    
    # Verify task attributes
    print("\nVerifying task attributes:")
    for task in new_manager.get_all_tasks():
        print(f"Title: {task.title}")
        print(f"Status: {task.status.name}")
        print(f"Priority: {task.priority.name}")
        print(f"Category: {task.category}")
        print(f"Due date: {task.due_date}")
        print("---")
    
    # Clean up
    print(f"\nCleaning up {csv_file}...")
    os.remove(csv_file)
    print("Done!")


if __name__ == "__main__":
    main()