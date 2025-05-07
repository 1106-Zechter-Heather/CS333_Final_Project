#!/usr/bin/env python3
"""Basic task creation and management."""

from src.task_manager import TaskManager


def main():
    """Demo basic task operations."""
    # Create a new task manager
    manager = TaskManager()
    
    # Add three tasks with different properties
    task1 = manager.add_task(
        title="Complete project documentation",
        description="Write full documentation for the task manager project",
        due_date="2023-12-15",
        priority="high",
        category="Work"
    )
    
    task2 = manager.add_task(
        title="Buy groceries",
        description="Milk, eggs, bread, vegetables",
        due_date="2023-11-05",
        priority="medium",
        category="Personal"
    )
    
    task3 = manager.add_task(
        title="Gym workout",
        description="30 min cardio + strength training",
        due_date="2023-11-06",
        priority="low",
        category="Health"
    )
    
    # Print all tasks
    print("All tasks:")
    for task in manager.get_all_tasks():
        print(f"- {task}")
    
    # Update a task
    print("\nUpdating task...")
    manager.update_task(
        task_id=task2.task_id,
        title="Buy groceries and household items",
        description="Milk, eggs, bread, vegetables, cleaning supplies",
        priority="high"
    )
    
    # Mark a task as completed
    print("Marking task as completed...")
    manager.mark_task_completed(task3.task_id)
    
    # Print updated tasks
    print("\nUpdated tasks:")
    for task in manager.get_all_tasks():
        print(f"- {task}")
    
    # Save tasks to a file
    file_path = "my_tasks.json"
    print(f"\nSaving tasks to {file_path}...")
    manager.save_to_file(file_path)
    
    # Load tasks from the file
    print(f"Loading tasks from {file_path}...")
    loaded_manager = TaskManager(file_path)
    
    # Verify loaded tasks
    print("\nLoaded tasks:")
    for task in loaded_manager.get_all_tasks():
        print(f"- {task}")
    
    # Delete a task
    print("\nDeleting a task...")
    loaded_manager.delete_task(task1.task_id)
    
    # Print remaining tasks
    print("\nRemaining tasks:")
    for task in loaded_manager.get_all_tasks():
        print(f"- {task}")


if __name__ == "__main__":
    main()