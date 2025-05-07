#!/usr/bin/env python3
"""
Integration example for Task Manager.

This example demonstrates how to integrate the Task Manager
with other tools like calendar applications or notification systems.
"""

import os
import json
import datetime
import subprocess
from src.task_manager import TaskManager


def export_to_calendar_format(tasks, file_path):
    """Export tasks to a calendar-compatible format (simplified iCal).
    
    Args:
        tasks: List of Task objects
        file_path: Path to save the calendar export
    """
    # Simple iCal-like format (not fully compliant)
    calendar_data = "BEGIN:VCALENDAR\n"
    calendar_data += "VERSION:2.0\n"
    calendar_data += "PRODID:-//Task Manager//Calendar Export//EN\n"
    
    for task in tasks:
        if not task.due_date:
            continue
            
        calendar_data += "BEGIN:VEVENT\n"
        calendar_data += f"UID:{task.task_id}\n"
        calendar_data += f"SUMMARY:{task.title}\n"
        
        if task.description:
            calendar_data += f"DESCRIPTION:{task.description}\n"
            
        # Format the date
        due_date = datetime.datetime.fromisoformat(task.due_date)
        date_str = due_date.strftime("%Y%m%dT%H%M%S")
        calendar_data += f"DTSTART:{date_str}\n"
        calendar_data += f"DTEND:{date_str}\n"
        
        # Add priority
        if task.priority.name == "HIGH":
            calendar_data += "PRIORITY:1\n"
        elif task.priority.name == "MEDIUM":
            calendar_data += "PRIORITY:5\n"
        else:
            calendar_data += "PRIORITY:9\n"
            
        calendar_data += f"CATEGORIES:{task.category}\n"
        calendar_data += "END:VEVENT\n"
    
    calendar_data += "END:VCALENDAR\n"
    
    with open(file_path, "w") as f:
        f.write(calendar_data)
    
    return file_path


def generate_notification_script(tasks, file_path):
    """Generate a script that could be used for system notifications.
    
    Args:
        tasks: List of Task objects
        file_path: Path to save the notification script
    """
    script = "#!/bin/bash\n\n"
    script += "# Generated notification script for upcoming tasks\n\n"
    
    # Add notifications for each task
    for task in tasks:
        if not task.due_date:
            continue
            
        # Only include upcoming tasks
        due_date = datetime.datetime.fromisoformat(task.due_date)
        today = datetime.datetime.now().date()
        
        if due_date.date() < today:
            # Skip overdue tasks
            continue
            
        priority = task.priority.name.lower()
        urgency = "critical" if priority == "high" else "normal"
        
        # Create notification command (works on Linux with notify-send)
        script += f"# Task: {task.title}\n"
        script += f'notify-send -u {urgency} "Task Due: {task.title}" '
        script += f'"Due date: {task.due_date} (Priority: {priority})"\n\n'
    
    with open(file_path, "w") as f:
        f.write(script)
    
    # Make the script executable
    os.chmod(file_path, 0o755)
    
    return file_path


def export_to_json_api_format(tasks, file_path):
    """Export tasks to a format suitable for API integrations.
    
    Args:
        tasks: List of Task objects
        file_path: Path to save the API export
    """
    api_data = {
        "tasks": [],
        "metadata": {
            "exported_at": datetime.datetime.now().isoformat(),
            "count": len(tasks)
        }
    }
    
    for task in tasks:
        task_data = {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority": task.priority.name.lower(),
            "category": task.category,
            "status": task.status.name.lower(),
            "created_at": task.created_at
        }
        api_data["tasks"].append(task_data)
    
    with open(file_path, "w") as f:
        json.dump(api_data, f, indent=2)
    
    return file_path


def main():
    """Run the integration example."""
    # Create a new task manager with sample tasks
    manager = TaskManager()
    
    # Add sample tasks
    manager.add_task(
        title="Important meeting",
        description="Quarterly review with the team",
        due_date=datetime.datetime.now().date().isoformat(),
        priority="high",
        category="Work"
    )
    
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date().isoformat()
    manager.add_task(
        title="Dentist appointment",
        description="Regular check-up",
        due_date=tomorrow,
        priority="medium",
        category="Health"
    )
    
    next_week = (datetime.datetime.now() + datetime.timedelta(days=7)).date().isoformat()
    manager.add_task(
        title="Submit report",
        description="Final project report submission",
        due_date=next_week,
        priority="high",
        category="Work"
    )
    
    # Get all tasks
    tasks = manager.get_all_tasks()
    
    # Calendar export
    calendar_file = "tasks.ics"
    print(f"Exporting tasks to calendar format: {calendar_file}")
    export_to_calendar_format(tasks, calendar_file)
    
    # Notification script
    script_file = "task_notifications.sh"
    print(f"Generating notification script: {script_file}")
    generate_notification_script(tasks, script_file)
    
    # API export
    api_file = "tasks_api.json"
    print(f"Exporting tasks to API format: {api_file}")
    export_to_json_api_format(tasks, api_file)
    
    # Demonstrate how to interact with the exports
    print("\nIntegration examples:")
    
    # Calendar file
    print(f"\nCalendar file ({calendar_file}) - first 5 lines:")
    with open(calendar_file, "r") as f:
        print("\n".join(f.readlines()[:5]))
    
    # Notification script
    print(f"\nNotification script ({script_file}) - first 5 lines:")
    with open(script_file, "r") as f:
        print("\n".join(f.readlines()[:5]))
    
    # API format
    print(f"\nAPI format ({api_file}) - preview:")
    with open(api_file, "r") as f:
        data = json.load(f)
        print(f"Exported {data['metadata']['count']} tasks at {data['metadata']['exported_at']}")
        print(f"First task: {data['tasks'][0]['title']}")
    
    # Clean up
    print("\nCleaning up integration example files...")
    for file in [calendar_file, script_file, api_file]:
        os.remove(file)
    
    print("Integration examples completed!")


if __name__ == "__main__":
    main()