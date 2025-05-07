"""Unit tests for utility functions."""

import unittest
import sys
import os
from datetime import datetime, date, timedelta

# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import (
    validate_date_format,
    convert_to_date,
    validate_priority,
    normalize_priority,
    is_task_overdue,
    format_task_display,
    format_task_list,
    _wrap_text,
    generate_task_report
)


class TestUtilFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.today = datetime.now().date().isoformat()
        self.tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
        self.yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        # Sample task dictionaries for testing
        self.task1 = {
            "task_id": "task-1",
            "title": "Test Task 1",
            "description": "This is test task 1",
            "due_date": self.tomorrow,
            "priority": "high",
            "category": "Testing",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.task2 = {
            "task_id": "task-2",
            "title": "Test Task 2",
            "description": "This is test task 2",
            "due_date": self.yesterday,
            "priority": "medium",
            "category": "Testing",
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        
        self.task3 = {
            "task_id": "task-3",
            "title": "Test Task 3 with a very long title that might need wrapping in some displays",
            "description": "This is test task 3 with a long description that should be wrapped when displayed",
            "due_date": None,
            "priority": "low",
            "category": "",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    
    def test_validate_date_format_valid(self):
        """Test validate_date_format with valid dates."""
        # Standard ISO format
        self.assertTrue(validate_date_format("2023-12-31"))
        
        # Today's date (dynamically generated)
        self.assertTrue(validate_date_format(self.today))
        
        # None is considered valid (for tasks with no due date)
        self.assertTrue(validate_date_format(None))
        
        # Leap year date
        self.assertTrue(validate_date_format("2024-02-29"))
        
        # First and last day of month/year
        self.assertTrue(validate_date_format("2023-01-01"))
        self.assertTrue(validate_date_format("2023-12-31"))
    
    def test_validate_date_format_invalid(self):
        """Test validate_date_format with invalid dates."""
        # Wrong format (MM-DD-YYYY)
        self.assertFalse(validate_date_format("12-31-2023"))
        
        # Wrong format (DD/MM/YYYY)
        self.assertFalse(validate_date_format("31/12/2023"))
        
        # Wrong separator
        self.assertFalse(validate_date_format("2023/12/31"))
        
        # Invalid month
        self.assertFalse(validate_date_format("2023-13-01"))
        
        # Invalid day
        self.assertFalse(validate_date_format("2023-02-30"))
        
        # Invalid format (with time)
        self.assertFalse(validate_date_format("2023-12-31 12:00:00"))
        
        # Invalid string
        self.assertFalse(validate_date_format("not a date"))
        
        # Empty string
        self.assertFalse(validate_date_format(""))
    
    def test_convert_to_date_valid(self):
        """Test convert_to_date with valid dates."""
        # Standard ISO format
        date_obj = convert_to_date("2023-12-31")
        self.assertIsInstance(date_obj, date)
        self.assertEqual(date_obj.year, 2023)
        self.assertEqual(date_obj.month, 12)
        self.assertEqual(date_obj.day, 31)
        
        # ISO format with time
        date_obj = convert_to_date("2023-12-31T12:00:00")
        self.assertIsInstance(date_obj, date)
        self.assertEqual(date_obj.year, 2023)
        self.assertEqual(date_obj.month, 12)
        self.assertEqual(date_obj.day, 31)
        
        # None returns None
        self.assertIsNone(convert_to_date(None))
    
    def test_convert_to_date_invalid(self):
        """Test convert_to_date with invalid dates."""
        # Wrong format
        with self.assertRaises(ValueError):
            convert_to_date("12-31-2023")
        
        # Invalid date
        with self.assertRaises(ValueError):
            convert_to_date("2023-02-30")
        
        # Invalid string
        with self.assertRaises(ValueError):
            convert_to_date("not a date")
    
    def test_validate_priority_valid(self):
        """Test validate_priority with valid priorities."""
        # Standard values
        self.assertTrue(validate_priority("high"))
        self.assertTrue(validate_priority("medium"))
        self.assertTrue(validate_priority("low"))
        
        # Case insensitive
        self.assertTrue(validate_priority("HIGH"))
        self.assertTrue(validate_priority("Medium"))
        self.assertTrue(validate_priority("Low"))
        
        # Abbreviated forms
        self.assertTrue(validate_priority("h"))
        self.assertTrue(validate_priority("m"))
        self.assertTrue(validate_priority("l"))
        self.assertTrue(validate_priority("med"))
        
        # With whitespace
        self.assertTrue(validate_priority(" high "))
        
        # Empty string (will use default)
        self.assertTrue(validate_priority(""))
    
    def test_validate_priority_invalid(self):
        """Test validate_priority with invalid priorities."""
        # Invalid values
        self.assertFalse(validate_priority("highest"))
        self.assertFalse(validate_priority("urgent"))
        self.assertFalse(validate_priority("normal"))
        self.assertFalse(validate_priority("1"))
        self.assertFalse(validate_priority("critical"))
    
    def test_normalize_priority_valid(self):
        """Test normalize_priority with valid priorities."""
        # Standard values
        self.assertEqual(normalize_priority("high"), "high")
        self.assertEqual(normalize_priority("medium"), "medium")
        self.assertEqual(normalize_priority("low"), "low")
        
        # Case insensitive
        self.assertEqual(normalize_priority("HIGH"), "high")
        self.assertEqual(normalize_priority("Medium"), "medium")
        self.assertEqual(normalize_priority("Low"), "low")
        
        # Abbreviated forms
        self.assertEqual(normalize_priority("h"), "high")
        self.assertEqual(normalize_priority("m"), "medium")
        self.assertEqual(normalize_priority("l"), "low")
        self.assertEqual(normalize_priority("med"), "medium")
        
        # With whitespace
        self.assertEqual(normalize_priority(" high "), "high")
        
        # Empty string (default is medium)
        self.assertEqual(normalize_priority(""), "medium")
    
    def test_normalize_priority_invalid(self):
        """Test normalize_priority with invalid priorities."""
        # Invalid values should raise ValueError
        with self.assertRaises(ValueError):
            normalize_priority("highest")
        
        with self.assertRaises(ValueError):
            normalize_priority("urgent")
        
        with self.assertRaises(ValueError):
            normalize_priority("normal")
        
        with self.assertRaises(ValueError):
            normalize_priority("1")
    
    def test_is_task_overdue(self):
        """Test is_task_overdue with various dates."""
        # Tasks due yesterday should be overdue
        self.assertTrue(is_task_overdue(self.yesterday, completed=False))
        
        # Tasks due today should not be overdue
        self.assertFalse(is_task_overdue(self.today, completed=False))
        
        # Tasks due tomorrow should not be overdue
        self.assertFalse(is_task_overdue(self.tomorrow, completed=False))
        
        # Completed tasks should not be overdue, even if due date is in the past
        self.assertFalse(is_task_overdue(self.yesterday, completed=True))
        
        # Tasks with no due date should not be overdue
        self.assertFalse(is_task_overdue(None, completed=False))
        
        # Invalid due date should not cause an error, should return False
        self.assertFalse(is_task_overdue("invalid", completed=False))
    
    def test_format_task_display_basic(self):
        """Test format_task_display with basic task information."""
        # Pending task due tomorrow
        display = format_task_display(self.task1)
        self.assertIn(self.task1["title"], display)
        self.assertIn("Due:", display)
        self.assertIn(self.task1["due_date"], display)
        self.assertIn("□", display)  # Pending marker
        self.assertIn("#Testing", display)  # Category
        
        # Completed task due yesterday
        display = format_task_display(self.task2)
        self.assertIn(self.task2["title"], display)
        self.assertIn("✓", display)  # Completed marker
        self.assertIn("Due:", display)
        
        # Task with no due date
        display = format_task_display(self.task3)
        self.assertIn(self.task3["title"], display)
        self.assertIn("□", display)  # Pending marker
        self.assertNotIn("Due:", display)
    
    def test_format_task_display_with_options(self):
        """Test format_task_display with various display options."""
        # Show task ID
        display = format_task_display(self.task1, show_id=True)
        self.assertIn(self.task1["task_id"][:8], display)
        
        # Show description
        display = format_task_display(self.task1, show_desc=True)
        self.assertIn(self.task1["description"], display)
        
        # Show both ID and description
        display = format_task_display(self.task1, show_id=True, show_desc=True)
        self.assertIn(self.task1["task_id"][:8], display)
        self.assertIn(self.task1["description"], display)
        
        # Overdue task
        overdue_task = self.task1.copy()
        overdue_task["due_date"] = self.yesterday
        display = format_task_display(overdue_task)
        self.assertIn("OVERDUE:", display)
    
    def test_format_task_list(self):
        """Test format_task_list with a list of tasks."""
        tasks = [self.task1, self.task2, self.task3]
        
        # Basic list
        display = format_task_list(tasks)
        for task in tasks:
            self.assertIn(task["title"], display)
        
        # Empty list
        display = format_task_list([])
        self.assertEqual(display, "No tasks found.")
        
        # List with IDs and descriptions
        display = format_task_list(tasks, show_ids=True, show_desc=True)
        for task in tasks:
            self.assertIn(task["title"], display)
            self.assertIn(task["description"], display)
            self.assertIn(task["task_id"][:8], display)
    
    def test_wrap_text(self):
        """Test _wrap_text with various texts."""
        # Short text (no wrapping needed)
        short_text = "This is a short text."
        self.assertEqual(_wrap_text(short_text, 80), short_text)
        
        # Long text requiring wrapping
        long_text = "This is a long text that should be wrapped into multiple lines because it exceeds the width limit."
        wrapped = _wrap_text(long_text, 20)
        self.assertGreater(wrapped.count("\n"), 0)
        
        # Empty text
        self.assertEqual(_wrap_text("", 80), "")
        
        # Text with exact width
        exact_text = "12345"
        self.assertEqual(_wrap_text(exact_text, 5), exact_text)
    
    def test_generate_task_report(self):
        """Test generate_task_report with various tasks."""
        tasks = [self.task1, self.task2, self.task3]
        
        # Create a task that's actually overdue (yesterday and pending)
        overdue_task = self.task2.copy()
        overdue_task["status"] = "pending"
        overdue_task["task_id"] = "task-overdue"
        modified_tasks = [self.task1, self.task2, self.task3, overdue_task]
        
        # Full report
        report = generate_task_report(modified_tasks)
        self.assertEqual(report["total"], 4)
        self.assertEqual(report["completed"], 1)
        self.assertEqual(report["pending"], 3)
        self.assertEqual(report["overdue"], 1)  # overdue_task is overdue
        self.assertEqual(report["completion_rate"], 25.0)
        
        # Report with only completed tasks
        report = generate_task_report(modified_tasks, completed_only=True)
        self.assertEqual(len(report["tasks"]), 1)
        self.assertEqual(report["tasks"][0]["task_id"], "task-2")
        
        # Report with only pending tasks
        report = generate_task_report(modified_tasks, pending_only=True)
        self.assertEqual(len(report["tasks"]), 3)
        
        # Report with only overdue tasks
        report = generate_task_report(modified_tasks, overdue_only=True)
        self.assertEqual(len(report["tasks"]), 1)
        self.assertEqual(report["tasks"][0]["task_id"], "task-overdue")
        
        # Empty list
        report = generate_task_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["completed"], 0)
        self.assertEqual(report["pending"], 0)
        self.assertEqual(report["overdue"], 0)
        self.assertEqual(report["completion_rate"], 0)


if __name__ == "__main__":
    unittest.main()