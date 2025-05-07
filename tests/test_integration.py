"""Integration tests for the Task Management System.

These tests verify that the components work together properly.
"""

import unittest
import os
import tempfile
import sys
import csv
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.task_manager import TaskManager
from src.task import Task, TaskStatus, TaskPriority
from src.utils import format_task_display, is_task_overdue


class TestTaskManagerIntegration(unittest.TestCase):
    """Integration tests for the TaskManager system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.json_file = os.path.join(self.temp_dir.name, "tasks.json")
        self.csv_file = os.path.join(self.temp_dir.name, "tasks.csv")
        
        # Create dates for testing
        self.today = datetime.now().date().isoformat()
        self.tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
        self.yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        # Initialize a TaskManager
        self.manager = TaskManager()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_create_and_retrieve_task(self):
        """Test creating a task and retrieving it, verifying persistence."""
        # 1. Create a task
        task = self.manager.add_task(
            title="Integration Test Task",
            description="This is a task for integration testing",
            due_date=self.tomorrow,
            priority="high",
            category="Integration"
        )
        
        # Save to file
        self.manager.save_to_file(self.json_file)
        
        # 2. Create a new TaskManager instance and load the file
        new_manager = TaskManager(self.json_file)
        
        # 3. Verify that the task was loaded correctly
        self.assertEqual(len(new_manager), 1)
        
        loaded_task = new_manager.get_task_by_id(task.task_id)
        self.assertIsNotNone(loaded_task)
        
        # 4. Verify all task attributes were preserved
        self.assertEqual(loaded_task.title, "Integration Test Task")
        self.assertEqual(loaded_task.description, "This is a task for integration testing")
        self.assertEqual(loaded_task.due_date, self.tomorrow)
        self.assertEqual(loaded_task.priority, TaskPriority.HIGH)
        self.assertEqual(loaded_task.category, "Integration")
        self.assertEqual(loaded_task.status, TaskStatus.PENDING)
        
        # 5. Check that the task can be found with different search methods
        self.assertEqual(len(new_manager.get_tasks_by_category("Integration")), 1)
        self.assertEqual(len(new_manager.get_tasks_by_priority("high")), 1)
        self.assertEqual(len(new_manager.get_tasks_by_due_date(self.tomorrow)), 1)
        self.assertEqual(len(new_manager.search_tasks("integration")), 1)
    
    def test_update_task_persistence(self):
        """Test updating a task and confirming changes persist through save/load."""
        # 1. Create a task
        task = self.manager.add_task(
            title="Task to Update",
            description="This task will be updated",
            due_date=self.tomorrow,
            priority="medium",
            category="Original"
        )
        
        # Save to file
        self.manager.save_to_file(self.json_file)
        
        # 2. Load task in a new manager
        manager1 = TaskManager(self.json_file)
        
        # 3. Update the task
        loaded_task = manager1.get_task_by_id(task.task_id)
        manager1.update_task(
            task_id=loaded_task.task_id,
            title="Updated Task",
            description="This task has been updated",
            due_date=self.today,
            priority="high",
            category="Updated"
        )
        
        # 4. Save the updated task
        manager1.save_to_file(self.json_file)
        
        # 5. Load in a third manager
        manager2 = TaskManager(self.json_file)
        
        # 6. Verify updates persisted
        updated_task = manager2.get_task_by_id(task.task_id)
        self.assertEqual(updated_task.title, "Updated Task")
        self.assertEqual(updated_task.description, "This task has been updated")
        self.assertEqual(updated_task.due_date, self.today)
        self.assertEqual(updated_task.priority, TaskPriority.HIGH)
        self.assertEqual(updated_task.category, "Updated")
        
        # 7. Verify task can be found with new values
        self.assertEqual(len(manager2.get_tasks_by_category("Updated")), 1)
        self.assertEqual(len(manager2.get_tasks_by_category("Original")), 0)
        self.assertEqual(len(manager2.get_tasks_by_priority("high")), 1)
        self.assertEqual(len(manager2.get_tasks_by_priority("medium")), 0)
    
    def test_delete_task_without_affecting_others(self):
        """Test deleting a task without affecting other tasks."""
        # 1. Create multiple tasks
        task1 = self.manager.add_task(
            title="Task 1",
            description="First task",
            due_date=self.yesterday,
            priority="low",
            category="Category1"
        )
        
        task2 = self.manager.add_task(
            title="Task 2",
            description="Second task",
            due_date=self.today,
            priority="medium",
            category="Category2"
        )
        
        task3 = self.manager.add_task(
            title="Task 3",
            description="Third task",
            due_date=self.tomorrow,
            priority="high",
            category="Category1"
        )
        
        # 2. Save to file
        self.manager.save_to_file(self.json_file)
        
        # 3. Load in a new manager
        new_manager = TaskManager(self.json_file)
        self.assertEqual(len(new_manager), 3)
        
        # 4. Delete the middle task
        success = new_manager.delete_task(task2.task_id)
        self.assertTrue(success)
        
        # 5. Verify only the middle task was deleted
        self.assertEqual(len(new_manager), 2)
        self.assertIsNotNone(new_manager.get_task_by_id(task1.task_id))
        self.assertIsNone(new_manager.get_task_by_id(task2.task_id))
        self.assertIsNotNone(new_manager.get_task_by_id(task3.task_id))
        
        # 6. Save changes
        new_manager.save_to_file(self.json_file)
        
        # 7. Load in another manager and verify
        third_manager = TaskManager(self.json_file)
        self.assertEqual(len(third_manager), 2)
        self.assertIsNotNone(third_manager.get_task_by_id(task1.task_id))
        self.assertIsNone(third_manager.get_task_by_id(task2.task_id))
        self.assertIsNotNone(third_manager.get_task_by_id(task3.task_id))
        
        # 8. Verify queries still work as expected
        self.assertEqual(len(third_manager.get_tasks_by_category("Category1")), 2)
        self.assertEqual(len(third_manager.get_tasks_by_category("Category2")), 0)
    
    def test_csv_export_import_preserves_data(self):
        """Test CSV export and import preserves all task data."""
        # 1. Create tasks with different attributes
        task1 = self.manager.add_task(
            title="Task with Special Chars: @#$%",
            description="Description with commas, quotes, and \"special\" characters",
            due_date=self.yesterday,
            priority="low",
            category="CSV Test"
        )
        
        # Add a task with a long description
        long_desc = "This is a very long description that spans multiple lines.\n"
        long_desc += "It has line breaks and other formatting that should be preserved.\n"
        long_desc += "The CSV export and import should handle this correctly."
        
        task2 = self.manager.add_task(
            title="Long Description Task",
            description=long_desc,
            due_date=self.tomorrow,
            priority="high",
            category="Long Content"
        )
        
        # Add a completed task
        task3 = self.manager.add_task(
            title="Completed Task",
            description="This task is already completed",
            due_date=self.today,
            priority="medium",
            category="Status Test"
        )
        self.manager.mark_task_completed(task3.task_id)
        
        # 2. Export to CSV
        success = self.manager.export_to_csv(self.csv_file)
        self.assertTrue(success)
        
        # 3. Verify the CSV file exists and has the right format
        self.assertTrue(os.path.exists(self.csv_file))
        
        with open(self.csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)
            
            # Check that all task data is present
            csv_task1 = next(row for row in rows if row["task_id"] == task1.task_id)
            self.assertEqual(csv_task1["title"], task1.title)
            self.assertEqual(csv_task1["description"], task1.description)
            
            csv_task2 = next(row for row in rows if row["task_id"] == task2.task_id)
            self.assertEqual(csv_task2["description"], long_desc)
            
            csv_task3 = next(row for row in rows if row["task_id"] == task3.task_id)
            self.assertEqual(csv_task3["status"], "completed")
        
        # 4. Create a new manager and import the CSV
        new_manager = TaskManager()
        success = new_manager.import_from_csv(self.csv_file)
        self.assertTrue(success)
        
        # 5. Verify all tasks were imported correctly
        self.assertEqual(len(new_manager), 3)
        
        # Find the imported tasks - IDs will be preserved
        imported_task1 = new_manager.get_task_by_id(task1.task_id)
        imported_task2 = new_manager.get_task_by_id(task2.task_id)
        imported_task3 = new_manager.get_task_by_id(task3.task_id)
        
        # Verify data integrity
        self.assertEqual(imported_task1.title, task1.title)
        self.assertEqual(imported_task1.description, task1.description)
        self.assertEqual(imported_task1.due_date, task1.due_date)
        self.assertEqual(imported_task1.priority, task1.priority)
        self.assertEqual(imported_task1.category, task1.category)
        
        self.assertEqual(imported_task2.description, long_desc)
        self.assertEqual(imported_task3.status, TaskStatus.COMPLETED)
        
        # 6. Test that the manager can be saved to JSON after CSV import
        new_manager.save_to_file(self.json_file)
        
        # 7. Load the JSON file and verify
        json_manager = TaskManager(self.json_file)
        self.assertEqual(len(json_manager), 3)
    
    def test_filtering_and_statistics(self):
        """Test task filtering and statistics calculations."""
        # 1. Create tasks with various attributes
        # Overdue task
        task1 = self.manager.add_task(
            title="Overdue Task",
            description="This task is overdue",
            due_date=self.yesterday,
            priority="high",
            category="Work"
        )
        
        # Pending task due today
        task2 = self.manager.add_task(
            title="Today's Task",
            description="This task is due today",
            due_date=self.today,
            priority="medium",
            category="Home"
        )
        
        # Future task
        task3 = self.manager.add_task(
            title="Future Task",
            description="This task is due in the future",
            due_date=self.tomorrow,
            priority="low",
            category="Work"
        )
        
        # Completed task
        task4 = self.manager.add_task(
            title="Completed Task",
            description="This task is already completed",
            due_date=self.yesterday,
            priority="medium",
            category="Personal"
        )
        self.manager.mark_task_completed(task4.task_id)
        
        # Cancelled task
        task5 = self.manager.add_task(
            title="Cancelled Task",
            description="This task is cancelled",
            due_date=self.tomorrow,
            priority="low",
            category="Work"
        )
        self.manager.mark_task_cancelled(task5.task_id)
        
        # 2. Test filtering methods
        # By status
        pending_tasks = self.manager.get_pending_tasks()
        self.assertEqual(len(pending_tasks), 3)
        
        completed_tasks = self.manager.get_completed_tasks()
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(completed_tasks[0].task_id, task4.task_id)
        
        cancelled_tasks = self.manager.get_cancelled_tasks()
        self.assertEqual(len(cancelled_tasks), 1)
        self.assertEqual(cancelled_tasks[0].task_id, task5.task_id)
        
        # By priority
        high_tasks = self.manager.get_tasks_by_priority("high")
        self.assertEqual(len(high_tasks), 1)
        self.assertEqual(high_tasks[0].task_id, task1.task_id)
        
        # By category
        work_tasks = self.manager.get_tasks_by_category("Work")
        self.assertEqual(len(work_tasks), 3)
        
        # By due date
        today_tasks = self.manager.get_tasks_by_due_date(self.today)
        self.assertEqual(len(today_tasks), 1)
        self.assertEqual(today_tasks[0].task_id, task2.task_id)
        
        # By search
        search_results = self.manager.search_tasks("overdue")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].task_id, task1.task_id)
        
        # 3. Test overdue detection
        overdue_tasks = self.manager.get_overdue_tasks()
        self.assertEqual(len(overdue_tasks), 1)  # Only task1 (task4 is completed)
        self.assertEqual(overdue_tasks[0].task_id, task1.task_id)
        
        # Verify using utils.is_task_overdue
        self.assertTrue(is_task_overdue(task1.due_date, completed=False))
        self.assertFalse(is_task_overdue(task4.due_date, completed=True))
        
        # 4. Test statistics
        stats = self.manager.get_stats()
        
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 3)
        self.assertEqual(stats["cancelled"], 1)
        self.assertEqual(stats["overdue"], 1)
        self.assertEqual(stats["completion_rate"], 20.0)
        
        # Category stats
        self.assertEqual(stats["categories"]["Work"], 3)
        self.assertEqual(stats["categories"]["Home"], 1)
        self.assertEqual(stats["categories"]["Personal"], 1)
        
        # Priority stats
        self.assertEqual(stats["priorities"]["high"], 1)
        self.assertEqual(stats["priorities"]["medium"], 2)
        self.assertEqual(stats["priorities"]["low"], 2)
        
        # 5. Test sorting
        sorted_by_due = self.manager.sort_tasks("due_date")
        self.assertEqual(sorted_by_due[0].task_id, task1.task_id)  # Yesterday
        self.assertEqual(sorted_by_due[1].task_id, task4.task_id)  # Yesterday (completed)
        
        sorted_by_priority = self.manager.sort_tasks("priority")
        # Low to high
        self.assertTrue(sorted_by_priority[0].priority.value <= sorted_by_priority[1].priority.value)
        self.assertTrue(sorted_by_priority[1].priority.value <= sorted_by_priority[2].priority.value)
    
    def test_command_line_workflow(self):
        """Test a complete workflow simulating CLI operations."""
        # This test verifies the full task management workflow using methods
        # that would be called by the CLI
        
        # 1. Initialize a new manager
        manager = TaskManager()
        
        # 2. Add a new task (similar to 'add' command)
        task = manager.add_task(
            title="CLI Task",
            description="Task added via CLI",
            due_date=self.tomorrow,
            priority="high",
            category="CLI Test"
        )
        task_id = task.task_id
        
        # Save to file (automatic after most CLI commands)
        manager.save_to_file(self.json_file)
        
        # 3. Reload the manager (simulating a new CLI invocation)
        manager = TaskManager(self.json_file)
        
        # 4. Update the task (similar to 'update' command)
        manager.update_task(
            task_id=task_id,
            title="Updated CLI Task",
            priority="medium"
        )
        manager.save_to_file(self.json_file)
        
        # 5. Mark as complete (similar to 'complete' command)
        manager = TaskManager(self.json_file)
        manager.mark_task_completed(task_id)
        manager.save_to_file(self.json_file)
        
        # 6. List tasks (similar to 'list' command)
        manager = TaskManager(self.json_file)
        tasks = manager.get_all_tasks()
        
        # Verify the task state
        self.assertEqual(len(tasks), 1)
        updated_task = tasks[0]
        self.assertEqual(updated_task.title, "Updated CLI Task")
        self.assertEqual(updated_task.priority, TaskPriority.MEDIUM)
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)
        
        # 7. Export to CSV (similar to 'export' command)
        manager.export_to_csv(self.csv_file)
        
        # 8. Delete the task (similar to 'delete' command)
        manager.delete_task(task_id)
        manager.save_to_file(self.json_file)
        
        # Verify it's deleted
        manager = TaskManager(self.json_file)
        self.assertEqual(len(manager), 0)
        
        # 9. Import from CSV (similar to 'import' command)
        manager.import_from_csv(self.csv_file)
        manager.save_to_file(self.json_file)
        
        # Verify the task was restored
        manager = TaskManager(self.json_file)
        self.assertEqual(len(manager), 1)
        
        # Verify the task has all the correct attributes
        restored_task = manager.get_all_tasks()[0]
        self.assertEqual(restored_task.title, "Updated CLI Task")
        self.assertEqual(restored_task.status, TaskStatus.COMPLETED)


class TestTaskDataIntegrity(unittest.TestCase):
    """Test data integrity across different operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.json_file = os.path.join(self.temp_dir.name, "tasks.json")
        self.csv_file = os.path.join(self.temp_dir.name, "tasks.csv")
        self.today = datetime.now().date().isoformat()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_round_trip_conversions(self):
        """Test data integrity through multiple conversion cycles."""
        # 1. Create tasks
        manager = TaskManager()
        task = manager.add_task(
            title="Round Trip Task",
            description="Testing round trip conversions",
            due_date=self.today,
            priority="high",
            category="Testing"
        )
        
        # 2. Convert to JSON
        manager.save_to_file(self.json_file)
        
        # 3. Export to CSV
        manager.export_to_csv(self.csv_file)
        
        # 4. Create a new manager and import the CSV
        csv_manager = TaskManager()
        csv_manager.import_from_csv(self.csv_file)
        
        # 5. Export back to a new JSON file
        json_file2 = os.path.join(self.temp_dir.name, "tasks2.json")
        csv_manager.save_to_file(json_file2)
        
        # 6. Load the new JSON file
        final_manager = TaskManager(json_file2)
        
        # 7. Verify data integrity through the conversions
        self.assertEqual(len(final_manager), 1)
        final_task = final_manager.get_all_tasks()[0]
        
        # Compare task attributes after the round trip
        self.assertEqual(final_task.title, task.title)
        self.assertEqual(final_task.description, task.description)
        self.assertEqual(final_task.due_date, task.due_date)
        self.assertEqual(final_task.priority, task.priority)
        self.assertEqual(final_task.category, task.category)
    
    def test_concurrent_modifications(self):
        """Test data handling with concurrent modifications."""
        # 1. Create an initial task
        manager1 = TaskManager()
        task = manager1.add_task(
            title="Original Task",
            description="Initial description",
            due_date=self.today,
            priority="medium",
            category="Original"
        )
        task_id = task.task_id
        
        # Save to file
        manager1.save_to_file(self.json_file)
        
        # 2. Create two managers with the same file
        manager2 = TaskManager(self.json_file)
        manager3 = TaskManager(self.json_file)
        
        # 3. Make different changes in each manager
        manager2.update_task(task_id, title="Updated by Manager 2")
        manager3.update_task(task_id, description="Updated by Manager 3")
        
        # 4. Save manager2's changes
        manager2.save_to_file(self.json_file)
        
        # 5. Save manager3's changes (overwriting manager2's changes)
        manager3.save_to_file(self.json_file)
        
        # 6. Load the file in a new manager
        final_manager = TaskManager(self.json_file)
        
        # 7. Verify the state (manager3's changes should prevail)
        final_task = final_manager.get_task_by_id(task_id)
        
        # Title should be original (not manager2's change)
        self.assertEqual(final_task.title, "Original Task")
        
        # Description should be manager3's change
        self.assertEqual(final_task.description, "Updated by Manager 3")


if __name__ == "__main__":
    unittest.main()