"""Unit tests for the Task class."""

import unittest
import json
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.task import Task, TaskStatus, TaskPriority


class TestTask(unittest.TestCase):
    """Test cases for the Task class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.today = datetime.now().date().isoformat()
        self.tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
        self.yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        # Create a sample task for testing
        self.task = Task(
            title="Test Task",
            description="This is a test task",
            due_date=self.tomorrow,
            priority="high",
            category="Testing",
        )
    
    def test_task_creation_normal(self):
        """Test creating a task with normal inputs."""
        task = Task(
            title="Normal Task",
            description="Description for a normal task",
            due_date=self.tomorrow,
            priority="medium",
            category="Normal Category",
        )
        
        self.assertEqual(task.title, "Normal Task")
        self.assertEqual(task.description, "Description for a normal task")
        self.assertEqual(task.due_date, self.tomorrow)
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.category, "Normal Category")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNotNone(task.task_id)
        self.assertIsNotNone(task.created_at)
    
    def test_task_creation_minimal(self):
        """Test creating a task with minimal inputs (just title)."""
        task = Task(title="Minimal Task")
        
        self.assertEqual(task.title, "Minimal Task")
        self.assertEqual(task.description, "")
        self.assertIsNone(task.due_date)
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.category, "")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNotNone(task.task_id)
        self.assertIsNotNone(task.created_at)
    
    def test_task_creation_empty_title(self):
        """Test that creating a task with an empty title raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="")
        
        with self.assertRaises(ValueError):
            Task(title="   ")
    
    def test_task_creation_date_formats(self):
        """Test creating tasks with various date formats."""
        # ISO format date
        task1 = Task(title="Date Task 1", due_date="2023-12-31")
        self.assertEqual(task1.due_date, "2023-12-31")
        
        # ISO format date with time
        task2 = Task(title="Date Task 2", due_date="2023-12-31T12:00:00")
        self.assertEqual(task2.due_date, "2023-12-31")
        
        # Invalid date format
        with self.assertRaises(ValueError):
            Task(title="Invalid Date", due_date="12/31/2023")
    
    def test_task_creation_priorities(self):
        """Test creating tasks with various priority values."""
        # Explicit priorities
        task_high = Task(title="High Priority", priority="high")
        self.assertEqual(task_high.priority, TaskPriority.HIGH)
        
        task_medium = Task(title="Medium Priority", priority="medium")
        self.assertEqual(task_medium.priority, TaskPriority.MEDIUM)
        
        task_low = Task(title="Low Priority", priority="low")
        self.assertEqual(task_low.priority, TaskPriority.LOW)
        
        # Abbreviated priorities
        task_h = Task(title="H Priority", priority="h")
        self.assertEqual(task_h.priority, TaskPriority.HIGH)
        
        task_m = Task(title="M Priority", priority="m")
        self.assertEqual(task_m.priority, TaskPriority.MEDIUM)
        
        task_l = Task(title="L Priority", priority="l")
        self.assertEqual(task_l.priority, TaskPriority.LOW)
        
        # Default priority (when not specified or empty)
        task_default = Task(title="Default Priority")
        self.assertEqual(task_default.priority, TaskPriority.MEDIUM)
        
        task_empty = Task(title="Empty Priority", priority="")
        self.assertEqual(task_empty.priority, TaskPriority.MEDIUM)
        
        # Invalid priority
        with self.assertRaises(ValueError):
            Task(title="Invalid Priority", priority="invalid")
    
    def test_title_getter_setter(self):
        """Test the title property getter and setter."""
        self.assertEqual(self.task.title, "Test Task")
        
        self.task.title = "Updated Title"
        self.assertEqual(self.task.title, "Updated Title")
        
        # Test validation
        with self.assertRaises(ValueError):
            self.task.title = ""
        
        with self.assertRaises(ValueError):
            self.task.title = "   "
    
    def test_description_getter_setter(self):
        """Test the description property getter and setter."""
        self.assertEqual(self.task.description, "This is a test task")
        
        self.task.description = "Updated description"
        self.assertEqual(self.task.description, "Updated description")
        
        # Empty description is allowed
        self.task.description = ""
        self.assertEqual(self.task.description, "")
    
    def test_due_date_getter_setter(self):
        """Test the due_date property getter and setter."""
        self.assertEqual(self.task.due_date, self.tomorrow)
        
        # Update due date
        new_date = "2023-12-31"
        self.task.due_date = new_date
        self.assertEqual(self.task.due_date, new_date)
        
        # Clear due date
        self.task.due_date = None
        self.assertIsNone(self.task.due_date)
        
        # Set an invalid date
        with self.assertRaises(ValueError):
            self.task.due_date = "12/31/2023"
    
    def test_priority_getter_setter(self):
        """Test the priority property getter and setter."""
        self.assertEqual(self.task.priority, TaskPriority.HIGH)
        
        # Update priority
        self.task.priority = "medium"
        self.assertEqual(self.task.priority, TaskPriority.MEDIUM)
        
        self.task.priority = "low"
        self.assertEqual(self.task.priority, TaskPriority.LOW)
        
        # Set an invalid priority
        with self.assertRaises(ValueError):
            self.task.priority = "invalid"
    
    def test_category_getter_setter(self):
        """Test the category property getter and setter."""
        self.assertEqual(self.task.category, "Testing")
        
        # Update category
        self.task.category = "Updated Category"
        self.assertEqual(self.task.category, "Updated Category")
        
        # Empty category is allowed
        self.task.category = ""
        self.assertEqual(self.task.category, "")
    
    def test_status_methods(self):
        """Test methods that change task status."""
        # Initial status is PENDING
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertFalse(self.task.is_completed())
        
        # Mark as complete
        self.task.mark_completed()
        self.assertEqual(self.task.status, TaskStatus.COMPLETED)
        self.assertTrue(self.task.is_completed())
        
        # Mark as pending
        self.task.mark_pending()
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertFalse(self.task.is_completed())
        
        # Mark as cancelled
        self.task.mark_cancelled()
        self.assertEqual(self.task.status, TaskStatus.CANCELLED)
        self.assertFalse(self.task.is_completed())
    
    def test_is_overdue(self):
        """Test the is_overdue method."""
        # Task due tomorrow should not be overdue
        self.task.due_date = self.tomorrow
        self.assertFalse(self.task.is_overdue())
        
        # Task due yesterday should be overdue
        self.task.due_date = self.yesterday
        self.assertTrue(self.task.is_overdue())
        
        # Completed task should not be overdue, even if due date is in the past
        self.task.mark_completed()
        self.assertFalse(self.task.is_overdue())
        
        # Task with no due date should not be overdue
        self.task.due_date = None
        self.assertFalse(self.task.is_overdue())
    
    def test_to_dict(self):
        """Test converting a task to a dictionary."""
        task_dict = self.task.to_dict()
        
        self.assertEqual(task_dict["title"], self.task.title)
        self.assertEqual(task_dict["description"], self.task.description)
        self.assertEqual(task_dict["due_date"], self.task.due_date)
        self.assertEqual(task_dict["priority"], self.task.priority.name.lower())
        self.assertEqual(task_dict["category"], self.task.category)
        self.assertEqual(task_dict["task_id"], self.task.task_id)
        self.assertEqual(task_dict["created_at"], self.task.created_at)
        self.assertEqual(task_dict["status"], self.task.status.name.lower())
    
    def test_to_json(self):
        """Test converting a task to JSON."""
        task_json = self.task.to_json()
        
        # Verify it's valid JSON
        task_dict = json.loads(task_json)
        
        self.assertEqual(task_dict["title"], self.task.title)
        self.assertEqual(task_dict["description"], self.task.description)
        self.assertEqual(task_dict["due_date"], self.task.due_date)
        self.assertEqual(task_dict["priority"], self.task.priority.name.lower())
        self.assertEqual(task_dict["category"], self.task.category)
    
    def test_from_dict(self):
        """Test creating a task from a dictionary."""
        task_dict = {
            "title": "Task From Dict",
            "description": "Created from dictionary",
            "due_date": "2023-12-31",
            "priority": "low",
            "category": "Testing",
            "task_id": "test-id-123",
            "created_at": "2023-01-01T12:00:00",
            "status": "completed",
        }
        
        task = Task.from_dict(task_dict)
        
        self.assertEqual(task.title, "Task From Dict")
        self.assertEqual(task.description, "Created from dictionary")
        self.assertEqual(task.due_date, "2023-12-31")
        self.assertEqual(task.priority, TaskPriority.LOW)
        self.assertEqual(task.category, "Testing")
        self.assertEqual(task.task_id, "test-id-123")
        self.assertEqual(task.created_at, "2023-01-01T12:00:00")
        self.assertEqual(task.status, TaskStatus.COMPLETED)
    
    def test_from_dict_minimal(self):
        """Test creating a task from a minimal dictionary."""
        task_dict = {
            "title": "Minimal Dict Task",
        }
        
        task = Task.from_dict(task_dict)
        
        self.assertEqual(task.title, "Minimal Dict Task")
        self.assertEqual(task.description, "")
        self.assertIsNone(task.due_date)
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.category, "")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIsNotNone(task.task_id)
        self.assertIsNotNone(task.created_at)
    
    def test_from_json(self):
        """Test creating a task from JSON."""
        json_str = json.dumps({
            "title": "Task From JSON",
            "description": "Created from JSON string",
            "due_date": "2023-12-31",
            "priority": "high",
            "category": "JSON Testing",
        })
        
        task = Task.from_json(json_str)
        
        self.assertEqual(task.title, "Task From JSON")
        self.assertEqual(task.description, "Created from JSON string")
        self.assertEqual(task.due_date, "2023-12-31")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.category, "JSON Testing")
    
    def test_from_json_invalid(self):
        """Test that creating a task from invalid JSON raises an exception."""
        with self.assertRaises(json.JSONDecodeError):
            Task.from_json("{invalid json")
    
    def test_str_representation(self):
        """Test the string representation of a task."""
        # Pending task
        self.task.mark_pending()
        str_repr = str(self.task)
        self.assertIn(self.task.title, str_repr)
        self.assertIn(self.task.due_date, str_repr)
        
        # Completed task
        self.task.mark_completed()
        str_repr = str(self.task)
        self.assertIn("✓", str_repr)
        
        # Task with no due date
        self.task.due_date = None
        str_repr = str(self.task)
        self.assertIn(self.task.title, str_repr)
        self.assertNotIn("Due:", str_repr)
    
    def test_repr_representation(self):
        """Test the detailed representation of a task."""
        repr_str = repr(self.task)
        self.assertIn(self.task.task_id, repr_str)
        self.assertIn(self.task.title, repr_str)
        self.assertIn(self.task.priority.name, repr_str)
        self.assertIn(self.task.status.name, repr_str)


if __name__ == "__main__":
    unittest.main()