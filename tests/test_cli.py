"""Unit tests for the CLI module."""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cli import setup_parser, handle_add, handle_list, handle_update, handle_complete
from src.cli import handle_pending, handle_cancel, handle_delete, handle_show
from src.cli import handle_export, handle_import, handle_merge, handle_stats
from src.cli import filter_tasks, main
from src.task_manager import TaskManager
from src.task import Task, TaskStatus, TaskPriority


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a temporary file for task storage
        self.task_file = os.path.join(self.temp_dir.name, "tasks.json")
        
        # Create a TaskManager with some test tasks
        self.manager = TaskManager()
        
        # Dates for testing
        self.today = datetime.now().date().isoformat()
        self.tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
        self.yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        # Add test tasks
        self.task1 = self.manager.add_task(
            title="Test Task 1",
            description="Description for task 1",
            due_date=self.tomorrow,
            priority="high",
            category="Work"
        )
        
        self.task2 = self.manager.add_task(
            title="Test Task 2",
            description="Description for task 2",
            due_date=self.yesterday,
            priority="medium",
            category="Home"
        )
        
        self.task3 = self.manager.add_task(
            title="Test Task 3",
            description="Description for task 3",
            priority="low",
            category="Work"
        )
        
        # Save tasks to the temporary file
        self.manager.save_to_file(self.task_file)
        
        # Create a mock argparse.Namespace for testing
        self.base_args = MagicMock()
        self.base_args.file = self.task_file
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_setup_parser(self):
        """Test that the parser is set up correctly."""
        parser = setup_parser()
        self.assertIsNotNone(parser)
        
        # Test that the parser has the expected commands
        args = parser.parse_args(['add', 'Test Task'])
        self.assertEqual(args.command, 'add')
        self.assertEqual(args.title, 'Test Task')
        
        args = parser.parse_args(['list'])
        self.assertEqual(args.command, 'list')
        
        args = parser.parse_args(['update', 'task-id'])
        self.assertEqual(args.command, 'update')
        self.assertEqual(args.task_id, 'task-id')
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_add(self, mock_stdout):
        """Test the add command handler."""
        args = self.base_args
        args.title = "New Test Task"
        args.description = "Description for new task"
        args.due_date = self.tomorrow
        args.priority = "high"
        args.category = "Test"
        
        handle_add(args, self.manager)
        
        # Check that the task was added
        self.assertEqual(len(self.manager), 4)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Task added:", output)
        self.assertIn("New Test Task", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_list(self, mock_stdout):
        """Test the list command handler."""
        args = self.base_args
        args.all = False
        args.completed = False
        args.pending = True
        args.cancelled = False
        args.priority = None
        args.category = None
        args.due_today = False
        args.due_before = None
        args.due_after = None
        args.overdue = False
        args.search = None
        args.sort_by = "due_date"
        args.reverse = False
        args.show_id = True
        args.show_description = True
        
        handle_list(args, self.manager)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Test Task 1", output)
        self.assertIn("Test Task 2", output)
        self.assertIn("Test Task 3", output)
        self.assertIn("Total:", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_update(self, mock_stdout):
        """Test the update command handler."""
        args = self.base_args
        args.task_id = self.task1.task_id
        args.title = "Updated Task 1"
        args.description = None
        args.due_date = None
        args.priority = None
        args.category = None
        
        handle_update(args, self.manager)
        
        # Check that the task was updated
        updated_task = self.manager.get_task_by_id(self.task1.task_id)
        self.assertEqual(updated_task.title, "Updated Task 1")
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Task updated:", output)
        self.assertIn("Updated Task 1", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_complete(self, mock_stdout):
        """Test the complete command handler."""
        args = self.base_args
        args.task_id = self.task1.task_id
        
        handle_complete(args, self.manager)
        
        # Check that the task was marked as completed
        completed_task = self.manager.get_task_by_id(self.task1.task_id)
        self.assertEqual(completed_task.status, TaskStatus.COMPLETED)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Task marked as complete:", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_pending(self, mock_stdout):
        """Test the pending command handler."""
        # First mark a task as completed
        self.manager.mark_task_completed(self.task1.task_id)
        
        args = self.base_args
        args.task_id = self.task1.task_id
        
        handle_pending(args, self.manager)
        
        # Check that the task was marked as pending
        pending_task = self.manager.get_task_by_id(self.task1.task_id)
        self.assertEqual(pending_task.status, TaskStatus.PENDING)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Task marked as pending:", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_cancel(self, mock_stdout):
        """Test the cancel command handler."""
        args = self.base_args
        args.task_id = self.task1.task_id
        
        handle_cancel(args, self.manager)
        
        # Check that the task was marked as cancelled
        cancelled_task = self.manager.get_task_by_id(self.task1.task_id)
        self.assertEqual(cancelled_task.status, TaskStatus.CANCELLED)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Task marked as cancelled:", output)
    
    @patch('builtins.input', return_value='y')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_delete(self, mock_stdout, mock_input):
        """Test the delete command handler."""
        args = self.base_args
        args.task_id = self.task1.task_id
        args.force = False
        
        handle_delete(args, self.manager)
        
        # Check that the task was deleted
        deleted_task = self.manager.get_task_by_id(self.task1.task_id)
        self.assertIsNone(deleted_task)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Task deleted:", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_show(self, mock_stdout):
        """Test the show command handler."""
        args = self.base_args
        args.task_id = self.task1.task_id
        
        handle_show(args, self.manager)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Title: Test Task 1", output)
        self.assertIn("Status: Pending", output)
        self.assertIn("Priority: High", output)
        self.assertIn("Category: Work", output)
        self.assertIn("Due date:", output)
        self.assertIn("Description:", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_export(self, mock_stdout):
        """Test the export command handler."""
        csv_file = os.path.join(self.temp_dir.name, "tasks.csv")
        
        args = self.base_args
        args.csv_file = csv_file
        
        handle_export(args, self.manager)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(csv_file))
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Tasks exported to CSV file:", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_import(self, mock_stdout):
        """Test the import command handler."""
        # First export tasks to a CSV file
        csv_file = os.path.join(self.temp_dir.name, "tasks.csv")
        self.manager.export_to_csv(csv_file)
        
        # Create a new manager to import into
        new_manager = TaskManager()
        
        args = self.base_args
        args.csv_file = csv_file
        args.merge = False
        
        handle_import(args, new_manager)
        
        # Check that the tasks were imported
        self.assertEqual(len(new_manager), 3)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Imported 3 task(s) from CSV file:", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_merge(self, mock_stdout):
        """Test the merge command handler."""
        # Create a second task file with different tasks
        second_file = os.path.join(self.temp_dir.name, "tasks2.json")
        second_manager = TaskManager()
        second_manager.add_task(
            title="Merged Task",
            description="This task should be merged",
            priority="high"
        )
        second_manager.save_to_file(second_file)
        
        args = self.base_args
        args.merge_file = second_file
        
        handle_merge(args, self.manager)
        
        # Check that the tasks were merged
        self.assertEqual(len(self.manager), 4)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Merged 1 task(s) from file:", output)
        self.assertIn("Total tasks: 4", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_stats(self, mock_stdout):
        """Test the stats command handler."""
        args = self.base_args
        
        handle_stats(args, self.manager)
        
        # Check the output
        output = mock_stdout.getvalue()
        self.assertIn("Task Statistics", output)
        self.assertIn("Total tasks: 3", output)
        self.assertIn("Completed: 0", output)
        self.assertIn("Pending: 3", output)
        self.assertIn("Categories", output)
        self.assertIn("Work: 2", output)
        self.assertIn("Home: 1", output)
        self.assertIn("Priorities", output)
        self.assertIn("High: 1", output)
        self.assertIn("Medium: 1", output)
        self.assertIn("Low: 1", output)
    
    def test_filter_tasks(self):
        """Test the filter_tasks function."""
        args = self.base_args
        args.all = False
        args.completed = False
        args.pending = True
        args.cancelled = False
        args.priority = None
        args.category = None
        args.due_today = False
        args.due_before = None
        args.due_after = None
        args.overdue = False
        args.search = None
        
        # All tasks are pending by default
        tasks = filter_tasks(args, self.manager)
        self.assertEqual(len(tasks), 3)
        
        # Filter by priority
        args.pending = True
        args.priority = "high"
        tasks = filter_tasks(args, self.manager)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, self.task1.task_id)
        
        # Filter by category
        args.pending = True
        args.priority = None
        args.category = "Work"
        tasks = filter_tasks(args, self.manager)
        self.assertEqual(len(tasks), 2)
        
        # Filter by search term
        args.pending = True
        args.category = None
        args.search = "Task 1"
        tasks = filter_tasks(args, self.manager)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, self.task1.task_id)
    
    @patch('src.cli.setup_parser')
    @patch('src.cli.handle_add')
    @patch('src.cli.handle_list')
    def test_main(self, mock_handle_list, mock_handle_add, mock_setup_parser):
        """Test the main function."""
        # Mock parser and args
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_setup_parser.return_value = mock_parser
        mock_parser.parse_args.return_value = mock_args
        
        # Test add command
        mock_args.command = "add"
        mock_args.file = self.task_file
        
        main()
        
        # Check that handle_add was called
        mock_handle_add.assert_called_once()
        
        # Reset mocks
        mock_handle_add.reset_mock()
        
        # Test list command
        mock_args.command = "list"
        
        main()
        
        # Check that handle_list was called
        mock_handle_list.assert_called_once()


if __name__ == "__main__":
    unittest.main()