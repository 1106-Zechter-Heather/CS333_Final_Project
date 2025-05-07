"""Task class for the task management system."""

from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, Optional
import json


class TaskPriority(Enum):
    """Priority levels for tasks."""
    
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    
    @classmethod
    def from_string(cls, priority_str: str) -> "TaskPriority":
        """Convert string to TaskPriority enum."""
        if not priority_str:
            return cls.MEDIUM
            
        normalized = priority_str.upper().strip()
        
        if normalized in ("LOW", "L"):
            return cls.LOW
        elif normalized in ("MEDIUM", "MED", "M"):
            return cls.MEDIUM
        elif normalized in ("HIGH", "H"):
            return cls.HIGH
        else:
            raise ValueError(
                f"Invalid priority '{priority_str}'. Must be one of: low, medium, high"
            )


class TaskStatus(Enum):
    """Enumeration of valid task status values."""
    
    PENDING = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class Task:
    """Represents a single task."""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: str = "medium",
        category: str = "",
        task_id: Optional[str] = None,
        created_at: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
    ):
        """Create a new task."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
            
        self._title = title.strip()
        self._description = description
        self._priority = TaskPriority.from_string(priority)
        self._category = category
        
        # Set task_id and created_at timestamp if not provided
        from uuid import uuid4
        self._task_id = task_id or str(uuid4())
        
        now = datetime.now().isoformat()
        self._created_at = created_at or now
        
        # Validate and set due date
        self._due_date = None
        if due_date:
            self.due_date = due_date  # Use the setter for validation
            
        self._status = status
    
    @property
    def title(self) -> str:
        """Get the task title."""
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        """Set the task title.
        
        Args:
            value: The new title.
            
        Raises:
            ValueError: If the title is empty.
        """
        if not value or not value.strip():
            raise ValueError("Task title cannot be empty")
        self._title = value.strip()
    
    @property
    def description(self) -> str:
        """Get the task description."""
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        """Set the task description."""
        self._description = value
    
    @property
    def due_date(self) -> Optional[str]:
        """Get the task due date."""
        return self._due_date
    
    @due_date.setter
    def due_date(self, value: Optional[str]) -> None:
        """Set the task due date.
        
        Args:
            value: The new due date in ISO format (YYYY-MM-DD) or None.
            
        Raises:
            ValueError: If the date format is invalid.
        """
        if value is None:
            self._due_date = None
            return
            
        try:
            # Validate the date format
            date_obj = datetime.fromisoformat(value.split("T")[0])
            # Store as ISO format date string
            self._due_date = date_obj.date().isoformat()
        except ValueError:
            raise ValueError(
                "Due date must be in ISO format (YYYY-MM-DD)"
            )
    
    @property
    def priority(self) -> TaskPriority:
        """Get the task priority."""
        return self._priority
    
    @priority.setter
    def priority(self, value: str) -> None:
        """Set the task priority.
        
        Args:
            value: The new priority level ("low", "medium", or "high").
            
        Raises:
            ValueError: If the priority is invalid.
        """
        self._priority = TaskPriority.from_string(value)
    
    @property
    def category(self) -> str:
        """Get the task category."""
        return self._category
    
    @category.setter
    def category(self, value: str) -> None:
        """Set the task category."""
        self._category = value
    
    @property
    def task_id(self) -> str:
        """Get the task ID."""
        return self._task_id
    
    @property
    def created_at(self) -> str:
        """Get the task creation timestamp."""
        return self._created_at
    
    @property
    def status(self) -> TaskStatus:
        """Get the task status."""
        return self._status
    
    @status.setter
    def status(self, value: TaskStatus) -> None:
        """Set the task status."""
        if not isinstance(value, TaskStatus):
            raise TypeError("Status must be a TaskStatus enum value")
        self._status = value
    
    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self._status = TaskStatus.COMPLETED
    
    def mark_pending(self) -> None:
        """Mark the task as pending (not completed)."""
        self._status = TaskStatus.PENDING
    
    def mark_cancelled(self) -> None:
        """Mark the task as cancelled."""
        self._status = TaskStatus.CANCELLED
    
    def is_completed(self) -> bool:
        """Check if the task is completed.
        
        Returns:
            True if the task is completed, False otherwise.
        """
        return self._status == TaskStatus.COMPLETED
    
    def is_overdue(self) -> bool:
        """Check if the task is overdue.
        
        Returns:
            True if the task has a due date in the past and is not completed,
            False otherwise.
        """
        if not self._due_date or self.is_completed():
            return False
            
        today = datetime.now().date()
        due = datetime.fromisoformat(self._due_date).date()
        return due < today
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary.
        
        Returns:
            A dictionary representation of the task.
        """
        return {
            "task_id": self._task_id,
            "title": self._title,
            "description": self._description,
            "due_date": self._due_date,
            "priority": self._priority.name.lower(),
            "category": self._category,
            "created_at": self._created_at,
            "status": self._status.name.lower(),
        }
    
    def to_json(self) -> str:
        """Convert the task to a JSON string.
        
        Returns:
            A JSON string representation of the task.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create a Task instance from a dictionary.
        
        Args:
            data: A dictionary containing task data.
            
        Returns:
            A new Task instance.
        """
        # Convert status string to TaskStatus enum
        status_str = data.get("status", "pending").upper()
        try:
            status = TaskStatus[status_str]
        except KeyError:
            status = TaskStatus.PENDING
            
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "medium"),
            category=data.get("category", ""),
            task_id=data.get("task_id"),
            created_at=data.get("created_at"),
            status=status,
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Task":
        """Create a Task instance from a JSON string.
        
        Args:
            json_str: A JSON string representing a task.
            
        Returns:
            A new Task instance.
            
        Raises:
            json.JSONDecodeError: If the JSON string is invalid.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """Get a string representation of the task.
        
        Returns:
            A string representation of the task.
        """
        status_marker = "✓" if self.is_completed() else " "
        priority_markers = {
            TaskPriority.LOW: "⭘",
            TaskPriority.MEDIUM: "⬤",
            TaskPriority.HIGH: "‼️",
        }
        
        priority_marker = priority_markers.get(self._priority, "")
        due_str = f" (Due: {self._due_date})" if self._due_date else ""
        
        return f"[{status_marker}] {priority_marker} {self._title}{due_str}"
    
    def __repr__(self) -> str:
        """Get a detailed string representation of the task.
        
        Returns:
            A detailed string representation of the task for debugging.
        """
        return (
            f"Task(id={self._task_id!r}, title={self._title!r}, "
            f"priority={self._priority.name}, status={self._status.name})"
        )