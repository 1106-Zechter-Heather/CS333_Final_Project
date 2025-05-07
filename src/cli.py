"""CLI for Task Manager."""

import argparse
import os
import sys
from datetime import datetime
from typing import List, Optional, Any, Dict

from .task_manager import TaskManager
from .task import Task
from .utils import format_task_display, format_task_list, validate_date_format


def setup_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Task Management System CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    # Add global arguments
    parser.add_argument(
        "--file", "-f",
        help="Path to the task file (JSON)",
        default=os.path.expanduser("~/.task_manager.json"),
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Command to execute",
    )
    subparsers.required = True
    
    # Add task command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new task",
    )
    add_parser.add_argument(
        "title",
        help="Task title",
    )
    add_parser.add_argument(
        "--description", "-d",
        help="Task description",
        default="",
    )
    add_parser.add_argument(
        "--due", "--due-date",
        help="Due date (YYYY-MM-DD)",
        dest="due_date",
    )
    add_parser.add_argument(
        "--priority", "-p",
        help="Priority (high, medium, low)",
        choices=["high", "medium", "low"],
        default="medium",
    )
    add_parser.add_argument(
        "--category", "-c",
        help="Task category or tag",
        default="",
    )
    
    # List tasks command
    list_parser = subparsers.add_parser(
        "list",
        help="List tasks",
    )
    list_parser.add_argument(
        "--all", "-a",
        help="Show all tasks (including completed)",
        action="store_true",
    )
    list_parser.add_argument(
        "--completed",
        help="Show only completed tasks",
        action="store_true",
    )
    list_parser.add_argument(
        "--pending",
        help="Show only pending tasks",
        action="store_true",
    )
    list_parser.add_argument(
        "--cancelled",
        help="Show only cancelled tasks",
        action="store_true",
    )
    list_parser.add_argument(
        "--priority", "-p",
        help="Filter by priority",
        choices=["high", "medium", "low"],
    )
    list_parser.add_argument(
        "--category", "-c",
        help="Filter by category",
    )
    list_parser.add_argument(
        "--due-today",
        help="Show tasks due today",
        action="store_true",
    )
    list_parser.add_argument(
        "--due-before",
        help="Show tasks due before a date (YYYY-MM-DD)",
        metavar="DATE",
    )
    list_parser.add_argument(
        "--due-after",
        help="Show tasks due after a date (YYYY-MM-DD)",
        metavar="DATE",
    )
    list_parser.add_argument(
        "--overdue",
        help="Show overdue tasks",
        action="store_true",
    )
    list_parser.add_argument(
        "--search", "-s",
        help="Search in task title and description",
        metavar="QUERY",
    )
    list_parser.add_argument(
        "--sort-by",
        help="Sort tasks by field",
        choices=["due_date", "priority", "title", "created_at", "category"],
        default="due_date",
    )
    list_parser.add_argument(
        "--reverse",
        help="Reverse the sort order",
        action="store_true",
    )
    list_parser.add_argument(
        "--show-id",
        help="Show task IDs",
        action="store_true",
    )
    list_parser.add_argument(
        "--show-description",
        help="Show task descriptions",
        action="store_true",
    )
    
    # Update task command
    update_parser = subparsers.add_parser(
        "update",
        help="Update an existing task",
    )
    update_parser.add_argument(
        "task_id",
        help="ID of the task to update",
    )
    update_parser.add_argument(
        "--title", "-t",
        help="New task title",
    )
    update_parser.add_argument(
        "--description", "-d",
        help="New task description",
        metavar="DESC",
    )
    update_parser.add_argument(
        "--due", "--due-date",
        help="New due date (YYYY-MM-DD or 'none' to clear)",
        dest="due_date",
        metavar="DATE",
    )
    update_parser.add_argument(
        "--priority", "-p",
        help="New priority (high, medium, low)",
        choices=["high", "medium", "low"],
    )
    update_parser.add_argument(
        "--category", "-c",
        help="New task category or tag (or 'none' to clear)",
        metavar="CAT",
    )
    
    # Complete task command
    complete_parser = subparsers.add_parser(
        "complete",
        help="Mark a task as complete",
    )
    complete_parser.add_argument(
        "task_id",
        help="ID of the task to mark as complete",
    )
    
    # Uncomplete task command
    pending_parser = subparsers.add_parser(
        "pending",
        help="Mark a task as pending (not complete)",
    )
    pending_parser.add_argument(
        "task_id",
        help="ID of the task to mark as pending",
    )
    
    # Cancel task command
    cancel_parser = subparsers.add_parser(
        "cancel",
        help="Mark a task as cancelled",
    )
    cancel_parser.add_argument(
        "task_id",
        help="ID of the task to mark as cancelled",
    )
    
    # Delete task command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task",
    )
    delete_parser.add_argument(
        "task_id",
        help="ID of the task to delete",
    )
    delete_parser.add_argument(
        "--force", "-f",
        help="Delete without confirmation",
        action="store_true",
    )
    
    # Show a single task command
    show_parser = subparsers.add_parser(
        "show",
        help="Show details of a single task",
    )
    show_parser.add_argument(
        "task_id",
        help="ID of the task to show",
    )
    
    # Export to CSV command
    export_parser = subparsers.add_parser(
        "export",
        help="Export tasks to CSV file",
    )
    export_parser.add_argument(
        "csv_file",
        help="Path to the CSV file to export to",
    )
    
    # Import from CSV command
    import_parser = subparsers.add_parser(
        "import",
        help="Import tasks from CSV file",
    )
    import_parser.add_argument(
        "csv_file",
        help="Path to the CSV file to import from",
    )
    import_parser.add_argument(
        "--merge",
        help="Merge imported tasks with existing tasks",
        action="store_true",
    )
    
    # Merge tasks from another file command
    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge tasks from another task file",
    )
    merge_parser.add_argument(
        "merge_file",
        help="Path to the task file to merge from",
    )
    
    # Show statistics command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show task statistics",
    )
    
    return parser


def handle_add(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'add' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    try:
        # Validate the due date if provided
        if args.due_date and not validate_date_format(args.due_date):
            print(f"Error: Invalid due date format: {args.due_date}")
            print("Due date should be in the format YYYY-MM-DD")
            sys.exit(1)
        
        # Add the task
        task = task_manager.add_task(
            title=args.title,
            description=args.description,
            due_date=args.due_date,
            priority=args.priority,
            category=args.category,
        )
        
        # Save the updated task list
        task_manager.save_to_file(args.file)
        
        print(f"Task added: {format_task_display(task.to_dict())}")
        print(f"Task ID: {task.task_id}")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def filter_tasks(args: argparse.Namespace, task_manager: TaskManager) -> List[Task]:
    """Filter tasks based on command line arguments.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
        
    Returns:
        A list of filtered Task objects.
    """
    tasks = task_manager.get_all_tasks()
    
    # Apply filters based on command line arguments
    if args.completed:
        tasks = task_manager.get_completed_tasks()
    elif args.pending:
        tasks = task_manager.get_pending_tasks()
    elif args.cancelled:
        tasks = task_manager.get_cancelled_tasks()
    elif not args.all:
        # By default, show only pending tasks
        tasks = task_manager.get_pending_tasks()
    
    # Filter by priority
    if args.priority:
        original_count = len(tasks)
        priority_tasks = task_manager.get_tasks_by_priority(args.priority)
        tasks = [task for task in tasks if task in priority_tasks]
        
    # Filter by category
    if args.category:
        original_count = len(tasks)
        category_tasks = task_manager.get_tasks_by_category(args.category)
        tasks = [task for task in tasks if task in category_tasks]
    
    # Filter by due date
    if args.due_today:
        today = datetime.now().date().isoformat()
        original_count = len(tasks)
        today_tasks = task_manager.get_tasks_by_due_date(today)
        tasks = [task for task in tasks if task in today_tasks]
        
    if args.due_before:
        if not validate_date_format(args.due_before):
            print(f"Error: Invalid date format: {args.due_before}")
            sys.exit(1)
        
        original_count = len(tasks)
        before_tasks = task_manager.get_tasks_due_before(args.due_before)
        tasks = [task for task in tasks if task in before_tasks]
        
    if args.due_after:
        if not validate_date_format(args.due_after):
            print(f"Error: Invalid date format: {args.due_after}")
            sys.exit(1)
        
        original_count = len(tasks)
        after_tasks = task_manager.get_tasks_due_after(args.due_after)
        tasks = [task for task in tasks if task in after_tasks]
    
    # Filter by overdue status
    if args.overdue:
        original_count = len(tasks)
        overdue_tasks = task_manager.get_overdue_tasks()
        tasks = [task for task in tasks if task in overdue_tasks]
    
    # Search in title and description
    if args.search:
        original_count = len(tasks)
        search_tasks = task_manager.search_tasks(args.search)
        tasks = [task for task in tasks if task in search_tasks]
    
    return tasks


def handle_list(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'list' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    try:
        # Get filtered tasks
        tasks = filter_tasks(args, task_manager)
        
        # Sort tasks
        sorted_tasks = task_manager.sort_tasks(args.sort_by, args.reverse)
        
        # Keep only the tasks that are in the filtered list
        sorted_tasks = [task for task in sorted_tasks if task in tasks]
        
        # Convert tasks to dictionaries for display
        task_dicts = [task.to_dict() for task in sorted_tasks]
        
        # Display the tasks
        if not task_dicts:
            print("No tasks found matching the criteria.")
            return
        
        print(format_task_list(
            task_dicts,
            show_ids=args.show_id,
            show_desc=args.show_description,
        ))
        
        print(f"\nTotal: {len(task_dicts)} task(s)")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_update(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'update' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    try:
        # Check that at least one field is being updated
        update_fields = [
            args.title,
            args.description,
            args.due_date,
            args.priority,
            args.category,
        ]
        
        if all(field is None for field in update_fields):
            print("Error: No fields specified for update.")
            print("Use --help to see available fields.")
            sys.exit(1)
        
        # Handle special case for clearing fields
        due_date = None
        if args.due_date == "none":
            due_date = None
        elif args.due_date:
            if not validate_date_format(args.due_date):
                print(f"Error: Invalid due date format: {args.due_date}")
                print("Due date should be in the format YYYY-MM-DD")
                sys.exit(1)
            due_date = args.due_date
        else:
            due_date = args.due_date  # Keep as None if not specified
        
        category = None
        if args.category == "none":
            category = ""
        else:
            category = args.category  # Keep as None if not specified
        
        # Update the task
        task = task_manager.update_task(
            task_id=args.task_id,
            title=args.title,
            description=args.description,
            due_date=due_date,
            priority=args.priority,
            category=category,
        )
        
        if not task:
            print(f"Error: No task found with ID: {args.task_id}")
            sys.exit(1)
        
        # Save the updated task list
        task_manager.save_to_file(args.file)
        
        print(f"Task updated: {format_task_display(task.to_dict())}")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_complete(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'complete' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    if not task_manager.mark_task_completed(args.task_id):
        print(f"Error: No task found with ID: {args.task_id}")
        sys.exit(1)
    
    # Save the updated task list
    task_manager.save_to_file(args.file)
    
    task = task_manager.get_task_by_id(args.task_id)
    print(f"Task marked as complete: {format_task_display(task.to_dict())}")


def handle_pending(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'pending' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    if not task_manager.mark_task_pending(args.task_id):
        print(f"Error: No task found with ID: {args.task_id}")
        sys.exit(1)
    
    # Save the updated task list
    task_manager.save_to_file(args.file)
    
    task = task_manager.get_task_by_id(args.task_id)
    print(f"Task marked as pending: {format_task_display(task.to_dict())}")


def handle_cancel(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'cancel' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    if not task_manager.mark_task_cancelled(args.task_id):
        print(f"Error: No task found with ID: {args.task_id}")
        sys.exit(1)
    
    # Save the updated task list
    task_manager.save_to_file(args.file)
    
    task = task_manager.get_task_by_id(args.task_id)
    print(f"Task marked as cancelled: {format_task_display(task.to_dict())}")


def handle_delete(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'delete' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    # Find the task to be deleted
    task = task_manager.get_task_by_id(args.task_id)
    
    if not task:
        print(f"Error: No task found with ID: {args.task_id}")
        sys.exit(1)
    
    # Confirm deletion if --force is not used
    if not args.force:
        task_display = format_task_display(task.to_dict())
        confirm = input(f"Delete task: {task_display}? (y/N) ")
        
        if confirm.lower() not in ("y", "yes"):
            print("Delete operation canceled.")
            sys.exit(0)
    
    # Delete the task
    task_manager.delete_task(args.task_id)
    
    # Save the updated task list
    task_manager.save_to_file(args.file)
    
    print(f"Task deleted: {task.title}")


def handle_show(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'show' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    task = task_manager.get_task_by_id(args.task_id)
    
    if not task:
        print(f"Error: No task found with ID: {args.task_id}")
        sys.exit(1)
    
    task_dict = task.to_dict()
    
    # Format the task details for display
    print(f"ID: {task_dict['task_id']}")
    print(f"Title: {task_dict['title']}")
    print(f"Status: {task_dict['status'].capitalize()}")
    print(f"Priority: {task_dict['priority'].capitalize()}")
    
    if task_dict['category']:
        print(f"Category: {task_dict['category']}")
    
    if task_dict['due_date']:
        is_overdue = task.is_overdue()
        due_text = f"OVERDUE: {task_dict['due_date']}" if is_overdue else task_dict['due_date']
        print(f"Due date: {due_text}")
    
    print(f"Created: {task_dict['created_at']}")
    
    if task_dict['description']:
        print("\nDescription:")
        print(task_dict['description'])


def handle_export(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'export' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    if task_manager.export_to_csv(args.csv_file):
        print(f"Tasks exported to CSV file: {args.csv_file}")
        print(f"Exported {len(task_manager)} task(s)")
    else:
        print(f"Error: Failed to export tasks to CSV file: {args.csv_file}")
        sys.exit(1)


def handle_import(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'import' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    try:
        if args.merge:
            # Create a temporary task manager to import the CSV
            temp_manager = TaskManager()
            if not temp_manager.import_from_csv(args.csv_file):
                print(f"Error: Failed to import tasks from CSV file: {args.csv_file}")
                sys.exit(1)
            
            # Convert to JSON file for merging
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_path = temp_file.name
            
            temp_manager.save_to_file(temp_path)
            
            # Merge with the existing tasks
            added = task_manager.merge_from_file(temp_path)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            # Save the merged tasks
            task_manager.save_to_file(args.file)
            
            print(f"Imported and merged {added} task(s) from CSV file: {args.csv_file}")
            print(f"Total tasks: {len(task_manager)}")
        
        else:
            # Replace existing tasks
            if not task_manager.import_from_csv(args.csv_file):
                print(f"Error: Failed to import tasks from CSV file: {args.csv_file}")
                sys.exit(1)
            
            # Save the imported tasks
            task_manager.save_to_file(args.file)
            
            print(f"Imported {len(task_manager)} task(s) from CSV file: {args.csv_file}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_merge(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'merge' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    try:
        added = task_manager.merge_from_file(args.merge_file)
        
        # Save the merged tasks
        task_manager.save_to_file(args.file)
        
        print(f"Merged {added} task(s) from file: {args.merge_file}")
        print(f"Total tasks: {len(task_manager)}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_stats(args: argparse.Namespace, task_manager: TaskManager) -> None:
    """Handle the 'stats' command.
    
    Args:
        args: Command line arguments.
        task_manager: TaskManager instance.
    """
    stats = task_manager.get_stats()
    
    print("Task Statistics")
    print("===============")
    print(f"Total tasks: {stats['total']}")
    print(f"Completed: {stats['completed']} ({stats['completion_rate']}%)")
    print(f"Pending: {stats['pending']}")
    print(f"Cancelled: {stats['cancelled']}")
    print(f"Overdue: {stats['overdue']}")
    
    if stats['categories']:
        print("\nCategories")
        print("----------")
        for category, count in sorted(stats['categories'].items()):
            print(f"{category}: {count} task(s)")
    
    print("\nPriorities")
    print("----------")
    print(f"High: {stats['priorities']['high']} task(s)")
    print(f"Medium: {stats['priorities']['medium']} task(s)")
    print(f"Low: {stats['priorities']['low']} task(s)")


def main() -> None:
    """Main entry point for the CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Create the task manager
    task_manager = TaskManager(args.file)
    
    # Handle the command
    if args.command == "add":
        handle_add(args, task_manager)
    elif args.command == "list":
        handle_list(args, task_manager)
    elif args.command == "update":
        handle_update(args, task_manager)
    elif args.command == "complete":
        handle_complete(args, task_manager)
    elif args.command == "pending":
        handle_pending(args, task_manager)
    elif args.command == "cancel":
        handle_cancel(args, task_manager)
    elif args.command == "delete":
        handle_delete(args, task_manager)
    elif args.command == "show":
        handle_show(args, task_manager)
    elif args.command == "export":
        handle_export(args, task_manager)
    elif args.command == "import":
        handle_import(args, task_manager)
    elif args.command == "merge":
        handle_merge(args, task_manager)
    elif args.command == "stats":
        handle_stats(args, task_manager)


if __name__ == "__main__":
    main()