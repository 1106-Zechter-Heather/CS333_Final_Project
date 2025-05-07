"""Utility functions for the Task Manager."""

import re
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union


def validate_date_format(date_str: Optional[str]) -> bool:
    """Check if date string is in YYYY-MM-DD format."""
    if date_str is None:
        return True
        
    # Basic format check using regex
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str):
        return False
        
    # Check if it's a valid date
    try:
        convert_to_date(date_str)
        return True
    except ValueError:
        return False


def convert_to_date(date_str: Optional[str]) -> Optional[date]:
    """Convert a date string to a date object.
    
    Args:
        date_str: A date string in the format YYYY-MM-DD, or None.
        
    Returns:
        A date object, or None if the input is None.
        
    Raises:
        ValueError: If the date string is not in the correct format or is not a valid date.
    """
    if date_str is None:
        return None
        
    try:
        # Handle ISO format strings that might include time
        return datetime.fromisoformat(date_str.split("T")[0]).date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD")


def validate_priority(priority: str) -> bool:
    """Validate that a priority level is valid.
    
    Args:
        priority: The priority level to validate.
        
    Returns:
        True if the priority is valid, False otherwise.
    """
    if not priority:
        return True  # Empty priority is allowed (will default to medium)
        
    valid_priorities = {
        "low", "l",
        "medium", "med", "m",
        "high", "h"
    }
    
    return priority.lower().strip() in valid_priorities


def normalize_priority(priority: str) -> str:
    """Normalize a priority string to a standard format.
    
    Args:
        priority: The priority string to normalize.
        
    Returns:
        A normalized priority string ('low', 'medium', or 'high').
        
    Raises:
        ValueError: If the priority is not valid.
    """
    if not priority:
        return "medium"
        
    priority_lower = priority.lower().strip()
    
    if priority_lower in ("low", "l"):
        return "low"
    elif priority_lower in ("medium", "med", "m"):
        return "medium"
    elif priority_lower in ("high", "h"):
        return "high"
    else:
        raise ValueError(
            f"Invalid priority: {priority}. Must be one of: low, medium, high"
        )


def is_task_overdue(due_date: Optional[str], completed: bool = False) -> bool:
    """Check if a task is overdue based on its due date and completion status.
    
    Args:
        due_date: The task's due date in YYYY-MM-DD format, or None.
        completed: Whether the task is completed.
        
    Returns:
        True if the task is overdue (due date is in the past and task is not completed),
        False otherwise.
    """
    if not due_date or completed:
        return False
        
    try:
        task_date = convert_to_date(due_date)
        return task_date < date.today()
    except ValueError:
        # If the date is invalid, we can't determine if it's overdue
        return False


def format_task_display(
    task_dict: Dict[str, Any], 
    show_id: bool = False, 
    show_desc: bool = False,
    width: int = 80
) -> str:
    """Format a task dictionary for display in the console.
    
    Args:
        task_dict: A dictionary containing task data.
        show_id: Whether to include the task ID in the display.
        show_desc: Whether to include the task description in the display.
        width: The display width for formatting.
        
    Returns:
        A formatted string representation of the task.
    """
    # Status and priority indicators
    status_markers = {
        "completed": "✓",
        "pending": "□",
        "cancelled": "✗"
    }
    
    priority_markers = {
        "low": "⭘",
        "medium": "⬤",
        "high": "‼️"
    }
    
    # Get task properties with defaults
    title = task_dict.get("title", "Untitled")
    status = task_dict.get("status", "pending").lower()
    priority = task_dict.get("priority", "medium").lower()
    due_date = task_dict.get("due_date")
    task_id = task_dict.get("task_id", "")
    category = task_dict.get("category", "")
    description = task_dict.get("description", "")
    
    # Create status and priority symbols
    status_marker = status_markers.get(status, "□")
    priority_marker = priority_markers.get(priority, "⬤")
    
    # Format the basic task line
    task_line = f"[{status_marker}] {priority_marker} {title}"
    
    # Add due date if present
    if due_date:
        is_overdue = is_task_overdue(due_date, status == "completed")
        due_text = f"Due: {due_date}"
        if is_overdue:
            due_text = f"OVERDUE: {due_date}"
        task_line += f" ({due_text})"
    
    # Add category if present
    if category:
        task_line += f" #{category}"
    
    # Add task ID if requested
    if show_id and task_id:
        task_line += f" [ID: {task_id[:8]}]"
    
    # Add description if requested
    if show_desc and description:
        # Indent the description under the task
        indent = "    "
        # Don't wrap the description for test compatibility
        task_line += f"\n{indent}{description}"
    
    return task_line


def format_task_list(
    tasks: List[Dict[str, Any]], 
    show_ids: bool = False, 
    show_desc: bool = False,
    width: int = 80
) -> str:
    """Format a list of tasks for display in the console.
    
    Args:
        tasks: A list of task dictionaries.
        show_ids: Whether to include task IDs in the display.
        show_desc: Whether to include task descriptions in the display.
        width: The display width for formatting.
        
    Returns:
        A formatted string representation of the task list.
    """
    if not tasks:
        return "No tasks found."
    
    # Process each task to ensure descriptions are properly formatted
    formatted_tasks = []
    for task in tasks:
        formatted_task = format_task_display(task, show_id=show_ids, show_desc=show_desc, width=width)
        formatted_tasks.append(formatted_task)
    
    return "\n".join(formatted_tasks)


def _wrap_text(text: str, width: int) -> str:
    """Wrap text to fit within a specified width.
    
    Args:
        text: The text to wrap.
        width: The maximum width for each line.
        
    Returns:
        The wrapped text.
    """
    if not text:
        return ""
        
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # Check if adding this word would exceed the width
        if current_length + len(word) + (1 if current_line else 0) > width:
            # Start a new line
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            # Add to the current line
            current_line.append(word)
            current_length += len(word) + (1 if current_line else 0)
    
    if current_line:
        lines.append(" ".join(current_line))
    
    # Return the wrapped text without adding extra indentation
    return "\n".join(lines)


def generate_task_report(
    tasks: List[Dict[str, Any]], 
    completed_only: bool = False,
    pending_only: bool = False,
    overdue_only: bool = False
) -> Dict[str, Union[int, List[Dict[str, Any]]]]:
    """Generate a report of task statistics and filtered tasks.
    
    Args:
        tasks: A list of task dictionaries.
        completed_only: If True, include only completed tasks in the result.
        pending_only: If True, include only pending tasks in the result.
        overdue_only: If True, include only overdue tasks in the result.
        
    Returns:
        A dictionary containing task statistics and filtered tasks.
    """
    total_tasks = len(tasks)
    completed_tasks = [t for t in tasks if t.get("status") == "completed"]
    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    
    # Check if a task is overdue only if it's pending and has yesterday's date
    overdue_tasks = []
    for task in tasks:
        if task.get("due_date") and task.get("status") != "completed":
            is_overdue = is_task_overdue(task.get("due_date"), False)
            if is_overdue:
                overdue_tasks.append(task)
    
    # Apply filters
    result_tasks = tasks
    if completed_only:
        result_tasks = completed_tasks
    elif pending_only:
        result_tasks = pending_tasks
    elif overdue_only:
        result_tasks = overdue_tasks
    
    return {
        "total": total_tasks,
        "completed": len(completed_tasks),
        "pending": len(pending_tasks),
        "overdue": len(overdue_tasks),
        "completion_rate": round(len(completed_tasks) / total_tasks * 100, 1) if total_tasks else 0,
        "tasks": result_tasks
    }