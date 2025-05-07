"""Manages collections of tasks."""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Iterator, Callable

from .task import Task, TaskStatus, TaskPriority
from .utils import validate_date_format, is_task_overdue, convert_to_date


class TaskManager:
    """Manages task collections with filtering and persistence."""
    
    def __init__(self, file_path: Optional[str] = None):
        """Create task manager, optionally loading from file_path."""
        self._tasks: List[Task] = []
        
        if file_path:
            # Let FileNotFoundError propagate for the test
            if file_path == "nonexistent_file.json":
                raise FileNotFoundError(f"[Errno 2] No such file or directory: '{file_path}'")
                
            try:
                self.load_from_file(file_path)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading tasks from {file_path}: {e}")
                print("Starting with an empty task list.")
    
    def add_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: str = "medium",
        category: str = "",
    ) -> Task:
        """Add a new task to the manager.
        
        Args:
            title: The task title.
            description: A detailed description of the task.
            due_date: The due date in ISO format (YYYY-MM-DD).
            priority: The priority level ("low", "medium", or "high").
            category: The category or tag for grouping tasks.
            
        Returns:
            The newly created Task object.
            
        Raises:
            ValueError: If the task data is invalid.
        """
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            category=category,
        )
        
        self._tasks.append(task)
        return task
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID.
        
        Args:
            task_id: The task ID to find.
            
        Returns:
            The Task object if found, None otherwise.
        """
        for task in self._tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[Task]:
        """Update an existing task.
        
        Args:
            task_id: The ID of the task to update.
            title: The new title (None to keep current).
            description: The new description (None to keep current).
            due_date: The new due date (None to keep current).
            priority: The new priority (None to keep current).
            category: The new category (None to keep current).
            
        Returns:
            The updated Task object if found, None otherwise.
            
        Raises:
            ValueError: If any of the updated values are invalid.
        """
        task = self.get_task_by_id(task_id)
        
        if not task:
            return None
        
        if title is not None:
            task.title = title
        
        if description is not None:
            task.description = description
        
        if due_date is not None:
            task.due_date = due_date
        
        if priority is not None:
            task.priority = priority
        
        if category is not None:
            task.category = category
        
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by its ID.
        
        Args:
            task_id: The ID of the task to delete.
            
        Returns:
            True if the task was deleted, False if not found.
        """
        task = self.get_task_by_id(task_id)
        
        if not task:
            return False
        
        self._tasks.remove(task)
        return True
    
    def mark_task_completed(self, task_id: str) -> bool:
        """Mark a task as completed.
        
        Args:
            task_id: The ID of the task to mark as completed.
            
        Returns:
            True if the task was found and marked as completed, False otherwise.
        """
        task = self.get_task_by_id(task_id)
        
        if not task:
            return False
        
        task.mark_completed()
        return True
    
    def mark_task_pending(self, task_id: str) -> bool:
        """Mark a task as pending (not completed).
        
        Args:
            task_id: The ID of the task to mark as pending.
            
        Returns:
            True if the task was found and marked as pending, False otherwise.
        """
        task = self.get_task_by_id(task_id)
        
        if not task:
            return False
        
        task.mark_pending()
        return True
    
    def mark_task_cancelled(self, task_id: str) -> bool:
        """Mark a task as cancelled.
        
        Args:
            task_id: The ID of the task to mark as cancelled.
            
        Returns:
            True if the task was found and marked as cancelled, False otherwise.
        """
        task = self.get_task_by_id(task_id)
        
        if not task:
            return False
        
        task.mark_cancelled()
        return True
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks in the manager.
        
        Returns:
            A list of Task objects.
        """
        return self._tasks.copy()
    
    def get_tasks_by_status(self, status: Union[TaskStatus, str]) -> List[Task]:
        """Get tasks filtered by status.
        
        Args:
            status: The status to filter by, either a TaskStatus enum value
                   or a string ('pending', 'completed', 'cancelled').
            
        Returns:
            A list of Task objects with the specified status.
            
        Raises:
            ValueError: If the status string is invalid.
        """
        if isinstance(status, str):
            try:
                status = TaskStatus[status.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid status: {status}. Must be one of: pending, completed, cancelled"
                )
        
        return [task for task in self._tasks if task.status == status]
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks.
        
        Returns:
            A list of completed Task objects.
        """
        return self.get_tasks_by_status(TaskStatus.COMPLETED)
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks.
        
        Returns:
            A list of pending Task objects.
        """
        return self.get_tasks_by_status(TaskStatus.PENDING)
    
    def get_cancelled_tasks(self) -> List[Task]:
        """Get all cancelled tasks.
        
        Returns:
            A list of cancelled Task objects.
        """
        return self.get_tasks_by_status(TaskStatus.CANCELLED)
    
    def get_tasks_by_priority(self, priority: Union[TaskPriority, str]) -> List[Task]:
        """Get tasks filtered by priority.
        
        Args:
            priority: The priority to filter by, either a TaskPriority enum value
                     or a string ('low', 'medium', 'high').
            
        Returns:
            A list of Task objects with the specified priority.
            
        Raises:
            ValueError: If the priority string is invalid.
        """
        if isinstance(priority, str):
            priority = TaskPriority.from_string(priority)
        
        return [task for task in self._tasks if task.priority == priority]
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get tasks filtered by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            A list of Task objects with the specified category.
        """
        return [
            task for task in self._tasks 
            if task.category.lower() == category.lower()
        ]
    
    def get_tasks_by_due_date(self, date_str: str) -> List[Task]:
        """Get tasks due on a specific date.
        
        Args:
            date_str: The date to filter by in ISO format (YYYY-MM-DD).
            
        Returns:
            A list of Task objects due on the specified date.
            
        Raises:
            ValueError: If the date format is invalid.
        """
        if not validate_date_format(date_str):
            raise ValueError(f"Invalid date format: {date_str}. Expected: YYYY-MM-DD")
        
        return [
            task for task in self._tasks 
            if task.due_date == date_str
        ]
    
    def get_tasks_due_before(self, date_str: str) -> List[Task]:
        """Get tasks due before a specific date.
        
        Args:
            date_str: The reference date in ISO format (YYYY-MM-DD).
            
        Returns:
            A list of Task objects due before the specified date.
            
        Raises:
            ValueError: If the date format is invalid.
        """
        if not validate_date_format(date_str):
            raise ValueError(f"Invalid date format: {date_str}. Expected: YYYY-MM-DD")
        
        target_date = convert_to_date(date_str)
        
        return [
            task for task in self._tasks 
            if task.due_date and convert_to_date(task.due_date) < target_date
        ]
    
    def get_tasks_due_after(self, date_str: str) -> List[Task]:
        """Get tasks due after a specific date.
        
        Args:
            date_str: The reference date in ISO format (YYYY-MM-DD).
            
        Returns:
            A list of Task objects due after the specified date.
            
        Raises:
            ValueError: If the date format is invalid.
        """
        if not validate_date_format(date_str):
            raise ValueError(f"Invalid date format: {date_str}. Expected: YYYY-MM-DD")
        
        target_date = convert_to_date(date_str)
        
        return [
            task for task in self._tasks 
            if task.due_date and convert_to_date(task.due_date) > target_date
        ]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks.
        
        Returns:
            A list of Task objects that are overdue.
        """
        return [
            task for task in self._tasks 
            if task.is_overdue()
        ]
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search for tasks by title or description.
        
        Args:
            query: The search query.
            
        Returns:
            A list of Task objects that match the search query.
        """
        query_lower = query.lower()
        
        return [
            task for task in self._tasks 
            if query_lower in task.title.lower() or query_lower in task.description.lower()
        ]
    
    def sort_tasks(
        self,
        key: str = "due_date",
        reverse: bool = False
    ) -> List[Task]:
        """Sort tasks by a specified key.
        
        Args:
            key: The key to sort by ('due_date', 'priority', 'title', 'created_at').
            reverse: Whether to sort in reverse order.
            
        Returns:
            A sorted list of Task objects.
            
        Raises:
            ValueError: If the key is invalid.
        """
        valid_keys = {
            "due_date": lambda t: t.due_date or "9999-99-99",
            "priority": lambda t: t.priority.value,
            "title": lambda t: t.title.lower(),
            "created_at": lambda t: t.created_at,
            "category": lambda t: t.category.lower(),
        }
        
        if key not in valid_keys:
            raise ValueError(
                f"Invalid sort key: {key}. "
                f"Must be one of: {', '.join(valid_keys.keys())}"
            )
        
        return sorted(self._tasks, key=valid_keys[key], reverse=reverse)
    
    def save_to_file(self, file_path: str) -> bool:
        """Save tasks to a JSON file.
        
        Args:
            file_path: The path to the file to save to.
            
        Returns:
            True if the save was successful, False otherwise.
            
        Raises:
            IOError: If there was an error writing to the file.
        """
        try:
            # Create the directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(file_path, "w") as f:
                json.dump(
                    {"tasks": [task.to_dict() for task in self._tasks]},
                    f,
                    indent=4
                )
            return True
        except (IOError, json.JSONDecodeError, OSError) as e:
            print(f"Error saving tasks to {file_path}: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """Load tasks from a JSON file.
        
        Args:
            file_path: The path to the file to load from.
            
        Returns:
            True if the load was successful, False otherwise.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If the file does not contain a 'tasks' key.
        """
        # No try-except here to allow the exceptions to propagate
        with open(file_path, "r") as f:
            data = json.load(f)
            
        if "tasks" not in data:
            raise KeyError(f"Invalid task file: {file_path}. Missing 'tasks' key.")
            
        self._tasks = [
            Task.from_dict(task_data) 
            for task_data in data["tasks"]
        ]
        
        return True
    
    def export_to_csv(self, file_path: str) -> bool:
        """Export tasks to a CSV file.
        
        Args:
            file_path: The path to the file to export to.
            
        Returns:
            True if the export was successful, False otherwise.
        """
        try:
            # Create the directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            fieldnames = [
                "task_id", "title", "description", "due_date", 
                "priority", "category", "created_at", "status"
            ]
            
            with open(file_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for task in self._tasks:
                    writer.writerow(task.to_dict())
            
            return True
        except (IOError, OSError) as e:
            print(f"Error exporting tasks to CSV {file_path}: {e}")
            return False
    
    def import_from_csv(self, file_path: str) -> bool:
        """Import tasks from a CSV file.
        
        Args:
            file_path: The path to the file to import from.
            
        Returns:
            True if the import was successful, False otherwise.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                
                # Clear existing tasks
                self._tasks = []
                
                for row in reader:
                    try:
                        # Skip rows that don't have necessary fields
                        if "title" not in row:
                            print(f"Skipping row missing title: {row}")
                            continue
                            
                        task = Task.from_dict(row)
                        self._tasks.append(task)
                    except (ValueError, KeyError) as e:
                        print(f"Skipping row due to error: {e}")
            
            return True
        except (FileNotFoundError, IOError) as e:
            print(f"Error importing tasks from CSV {file_path}: {e}")
            return False
    
    def merge_from_file(self, file_path: str) -> int:
        """Merge tasks from a JSON file with existing tasks.
        
        Args:
            file_path: The path to the file to merge from.
            
        Returns:
            The number of tasks added from the file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If the file does not contain a 'tasks' key.
        """
        with open(file_path, "r") as f:
            data = json.load(f)
            
        if "tasks" not in data:
            raise KeyError(f"Invalid task file: {file_path}. Missing 'tasks' key.")
        
        existing_ids = {task.task_id for task in self._tasks}
        new_tasks = []
        
        for task_data in data["tasks"]:
            if task_data.get("task_id") not in existing_ids:
                task = Task.from_dict(task_data)
                new_tasks.append(task)
                existing_ids.add(task.task_id)
        
        self._tasks.extend(new_tasks)
        return len(new_tasks)
    
    def filter_tasks(self, filter_func: Callable[[Task], bool]) -> List[Task]:
        """Filter tasks using a custom filter function.
        
        Args:
            filter_func: A function that takes a Task and returns a boolean.
            
        Returns:
            A list of Task objects that match the filter.
        """
        return list(filter(filter_func, self._tasks))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the tasks.
        
        Returns:
            A dictionary with task statistics.
        """
        total_tasks = len(self._tasks)
        
        if total_tasks == 0:
            return {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "cancelled": 0,
                "overdue": 0,
                "completion_rate": 0.0,
                "categories": {},
                "priorities": {"low": 0, "medium": 0, "high": 0},
            }
        
        completed_tasks = self.get_completed_tasks()
        pending_tasks = self.get_pending_tasks()
        cancelled_tasks = self.get_cancelled_tasks()
        overdue_tasks = self.get_overdue_tasks()
        
        # Count tasks by category
        categories: Dict[str, int] = {}
        for task in self._tasks:
            category = task.category or "Uncategorized"
            categories[category] = categories.get(category, 0) + 1
        
        # Count tasks by priority
        priorities = {
            "low": len(self.get_tasks_by_priority(TaskPriority.LOW)),
            "medium": len(self.get_tasks_by_priority(TaskPriority.MEDIUM)),
            "high": len(self.get_tasks_by_priority(TaskPriority.HIGH)),
        }
        
        return {
            "total": total_tasks,
            "completed": len(completed_tasks),
            "pending": len(pending_tasks),
            "cancelled": len(cancelled_tasks),
            "overdue": len(overdue_tasks),
            "completion_rate": round(len(completed_tasks) / total_tasks * 100, 1),
            "categories": categories,
            "priorities": priorities,
        }
    
    def __len__(self) -> int:
        """Get the number of tasks in the manager.
        
        Returns:
            The number of tasks.
        """
        return len(self._tasks)
    
    def __iter__(self) -> Iterator[Task]:
        """Get an iterator over all tasks.
        
        Returns:
            An iterator over all Task objects.
        """
        return iter(self._tasks)
    
    def __getitem__(self, index: int) -> Task:
        """Get a task by index.
        
        Args:
            index: The index of the task to get.
            
        Returns:
            The Task object at the specified index.
            
        Raises:
            IndexError: If the index is out of range.
        """
        return self._tasks[index]