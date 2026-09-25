"""
planner.py
----------
Core task-management logic for the Smart Study Planner:
- adding / viewing / editing / deleting / completing tasks
- the "smart" priority scoring algorithm
- deadline alerts
- progress tracking and statistics

Each task is stored as a dictionary (see storage.py for the exact shape).
"""

from datetime import datetime

from utils import (
    get_non_empty_string,
    get_positive_float,
    get_valid_date,
    get_choice_from_list,
    get_yes_no,
    days_between,
    today,
)
from storage import get_next_task_id

PRIORITY_LEVELS = {"Low": 1, "Medium": 2, "High": 3}
DIFFICULTY_LEVELS = {"Easy": 1, "Medium": 2, "Hard": 3}


# ---------------------------------------------------------------------------
# TASK CREATION / EDITING / DELETION
# ---------------------------------------------------------------------------

def add_task(tasks):
    """Prompt the user for all task fields and append a new task dictionary."""
    print("\n--- Add New Study Task ---")
    subject = get_non_empty_string("Subject name: ")
    topic = get_non_empty_string("Topic / task name: ")
    deadline = get_valid_date("Deadline date")
    estimated_hours = get_positive_float("Estimated hours required: ")
    priority = get_choice_from_list("Priority", ["Low", "Medium", "High"])
    difficulty = get_choice_from_list("Difficulty", ["Easy", "Medium", "Hard"])

    new_task = {
        "id": get_next_task_id(tasks),
        "subject": subject,
        "topic": topic,
        "deadline": deadline.isoformat(),
        "estimated_hours": estimated_hours,
        "hours_completed": 0.0,
        "priority": priority,
        "difficulty": difficulty,
        "completed": False,
    }
    tasks.append(new_task)
    print(f"\nTask added: {subject} - {topic} (ID {new_task['id']})")


def find_task_by_id(tasks, task_id):
    """Return the task dict with the given id, or None if not found."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def edit_task(tasks):
    """Let the user pick a task by ID and change any of its fields."""
    if not tasks:
        print("\nThere are no tasks to edit yet.")
        return

    view_tasks(tasks)
    task_id = _ask_for_existing_task_id(tasks, "Enter the ID of the task to edit: ")
    if task_id is None:
        return

    task = find_task_by_id(tasks, task_id)
    print(f"\nEditing '{task['subject']} - {task['topic']}'. Leave a field blank to keep it unchanged.")

    new_subject = input(f"Subject name [{task['subject']}]: ").strip()
    if new_subject:
        task["subject"] = new_subject

    new_topic = input(f"Topic / task name [{task['topic']}]: ").strip()
    if new_topic:
        task["topic"] = new_topic

    if get_yes_no("Change the deadline?"):
        task["deadline"] = get_valid_date("New deadline date").isoformat()

    if get_yes_no("Change the estimated hours required?"):
        task["estimated_hours"] = get_positive_float("New estimated hours: ")

    if get_yes_no("Change the priority?"):
        task["priority"] = get_choice_from_list("New priority", ["Low", "Medium", "High"])

    if get_yes_no("Change the difficulty?"):
        task["difficulty"] = get_choice_from_list("New difficulty", ["Easy", "Medium", "Hard"])

    print("\nTask updated successfully.")


def delete_task(tasks):
    """Let the user pick a task by ID and remove it from the list."""
    if not tasks:
        print("\nThere are no tasks to delete yet.")
        return

    view_tasks(tasks)
    task_id = _ask_for_existing_task_id(tasks, "Enter the ID of the task to delete: ")
    if task_id is None:
        return

    task = find_task_by_id(tasks, task_id)
    if get_yes_no(f"Are you sure you want to delete '{task['subject']} - {task['topic']}'?"):
        tasks.remove(task)
        print("Task deleted.")
    else:
        print("Deletion cancelled.")


def mark_task_complete(tasks):
    """Let the user pick a task by ID and mark it fully completed."""
    if not tasks:
        print("\nThere are no tasks yet.")
        return

    view_tasks(tasks)
    task_id = _ask_for_existing_task_id(tasks, "Enter the ID of the task to mark complete: ")
    if task_id is None:
        return

    task = find_task_by_id(tasks, task_id)
    task["completed"] = True
    task["hours_completed"] = task["estimated_hours"]
    print(f"'{task['subject']} - {task['topic']}' marked as completed.")


def _ask_for_existing_task_id(tasks, prompt):
    """
    Shared helper: ask for a task ID and validate that it exists.
    Returns the integer ID, or None if the user's input was invalid.
    """
    raw = input(prompt).strip()
    if not raw.isdigit():
        print("Please enter a numeric task ID.")
        return None
    task_id = int(raw)
    if find_task_by_id(tasks, task_id) is None:
        print("No task found with that ID.")
        return None
    return task_id


# ---------------------------------------------------------------------------
# VIEWING TASKS
# ---------------------------------------------------------------------------

def view_tasks(tasks):
    """Print every task in a readable table-like format."""
    if not tasks:
        print("\nNo tasks added yet.")
        return

    print("\n{:<4}{:<14}{:<22}{:<12}{:<8}{:<9}{:<9}{:<10}".format(
        "ID", "Subject", "Topic", "Deadline", "Hours", "Priority", "Difficulty", "Status"
    ))
    print("-" * 90)
    for task in tasks:
        status = "Done" if task["completed"] else "Pending"
        print("{:<4}{:<14}{:<22}{:<12}{:<8}{:<9}{:<9}{:<10}".format(
            task["id"],
            task["subject"][:13],
            task["topic"][:21],
            task["deadline"],
            task["estimated_hours"],
            task["priority"],
            task["difficulty"],
            status,
        ))


# ---------------------------------------------------------------------------
# SMART PRIORITY SCORING
# ---------------------------------------------------------------------------

def calculate_priority_score(task, reference_date=None):
    """
    Calculate a numeric priority score for a task. Higher = more urgent
    and important, and should be studied sooner.

    Formula:
        score = (priority_level * 10)
              + (difficulty_level * 5)
              + urgency_score
              + remaining_hours

    Where:
        priority_level   : Low=1, Medium=2, High=3
        difficulty_level : Easy=1, Medium=2, Hard=3
        urgency_score     : 100 if overdue, otherwise
                             max(0, 60 - days_left * 3)
                             (so a task due tomorrow scores much higher
                             urgency than one due in 3 weeks)
        remaining_hours   : estimated_hours - hours_completed
                             (bigger remaining workloads get a small
                             boost since they need an earlier start)

    Completed tasks always score 0, so they never appear in schedules
    or "most urgent" statistics.
    """
    if task["completed"]:
        return 0

    if reference_date is None:
        reference_date = today()

    deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
    days_left = days_between(reference_date, deadline)

    priority_level = PRIORITY_LEVELS.get(task["priority"], 1)
    difficulty_level = DIFFICULTY_LEVELS.get(task["difficulty"], 1)
    remaining_hours = max(0.0, task["estimated_hours"] - task["hours_completed"])

    if days_left < 0:
        urgency_score = 100  # overdue: always top priority
    else:
        urgency_score = max(0, 60 - (days_left * 3))

    score = (priority_level * 10) + (difficulty_level * 5) + urgency_score + remaining_hours
    return round(score, 2)


def get_sorted_tasks_by_priority(tasks):
    """Return only incomplete tasks, sorted from highest to lowest priority score."""
    incomplete = [t for t in tasks if not t["completed"]]
    return sorted(incomplete, key=lambda t: calculate_priority_score(t), reverse=True)


# ---------------------------------------------------------------------------
# DEADLINE ALERTS
# ---------------------------------------------------------------------------

def check_deadline_alerts(tasks, student):
    """
    Print warnings for:
    - overdue tasks
    - tasks due tomorrow
    - tasks due within 3 days
    - tasks whose remaining hours exceed the time realistically left
      before their deadline (given the student's daily study hours
      and study days per week)
    """
    if not tasks:
        print("\nNo tasks to check.")
        return

    ref = today()
    overdue, due_tomorrow, due_soon, overloaded = [], [], [], []

    # Roughly how many of the student's study days occur per 7-day week,
    # used to estimate hours realistically available before a deadline.
    study_days_per_week = max(1, len(student.get("study_days", [])))
    daily_hours = student.get("daily_hours", 0)

    for task in tasks:
        if task["completed"]:
            continue

        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
        days_left = days_between(ref, deadline)
        remaining_hours = max(0.0, task["estimated_hours"] - task["hours_completed"])

        if days_left < 0:
            overdue.append(task)
            continue
        elif days_left == 1:
            due_tomorrow.append(task)
        elif days_left <= 3:
            due_soon.append(task)

        # Estimate realistic available hours before the deadline.
        weeks_left = days_left / 7
        available_hours = weeks_left * study_days_per_week * daily_hours
        if remaining_hours > available_hours:
            overloaded.append((task, remaining_hours, available_hours))

    if overdue:
        print("\n[OVERDUE]")
        for t in overdue:
            print(f"  - {t['subject']} - {t['topic']} (was due {t['deadline']})")

    if due_tomorrow:
        print("\n[DUE TOMORROW]")
        for t in due_tomorrow:
            print(f"  - {t['subject']} - {t['topic']}")

    if due_soon:
        print("\n[DUE WITHIN 3 DAYS]")
        for t in due_soon:
            print(f"  - {t['subject']} - {t['topic']} (due {t['deadline']})")

    if overloaded:
        print("\n[NOT ENOUGH TIME WARNING]")
        for t, remaining_hours, available_hours in overloaded:
            print(f"  - {t['subject']} - {t['topic']}: needs {remaining_hours:.1f}h, "
                  f"only ~{available_hours:.1f}h realistically available before the deadline")

    if not (overdue or due_tomorrow or due_soon or overloaded):
        print("\nNo urgent deadline warnings right now. You're on track!")


# ---------------------------------------------------------------------------
# PROGRESS TRACKING
# ---------------------------------------------------------------------------

def get_progress_report(tasks):
    """Return a dictionary summarizing overall progress."""
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t["completed"]])
    pending_tasks = total_tasks - completed_tasks

    total_hours = sum(t["estimated_hours"] for t in tasks)
    completed_hours = sum(t["hours_completed"] for t in tasks)
    remaining_hours = total_hours - completed_hours

    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks else 0.0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_percentage": round(completion_percentage, 1),
        "total_hours": round(total_hours, 1),
        "completed_hours": round(completed_hours, 1),
        "remaining_hours": round(remaining_hours, 1),
    }


def print_progress_report(tasks):
    """Print the progress report in a readable format."""
    report = get_progress_report(tasks)
    print("\n--- Progress Report ---")
    print(f"Total tasks        : {report['total_tasks']}")
    print(f"Completed tasks    : {report['completed_tasks']}")
    print(f"Pending tasks      : {report['pending_tasks']}")
    print(f"Completion         : {report['completion_percentage']}%")
    print(f"Total study hours  : {report['total_hours']}")
    print(f"Hours completed    : {report['completed_hours']}")
    print(f"Hours remaining    : {report['remaining_hours']}")


# ---------------------------------------------------------------------------
# STATISTICS
# ---------------------------------------------------------------------------

def get_statistics(tasks):
    """
    Build a statistics dictionary:
    - subject-wise study hours (dict: subject -> total estimated hours)
    - completed vs pending counts
    - most urgent subject (highest priority score among incomplete tasks)
    - most difficult subject (task with the highest difficulty level)
    - total planned hours
    """
    subject_hours = {}
    for task in tasks:
        subject_hours[task["subject"]] = subject_hours.get(task["subject"], 0) + task["estimated_hours"]

    completed = [t for t in tasks if t["completed"]]
    pending = [t for t in tasks if not t["completed"]]

    most_urgent_subject = None
    if pending:
        most_urgent_task = max(pending, key=lambda t: calculate_priority_score(t))
        most_urgent_subject = most_urgent_task["subject"]

    most_difficult_subject = None
    if tasks:
        most_difficult_task = max(tasks, key=lambda t: DIFFICULTY_LEVELS.get(t["difficulty"], 0))
        most_difficult_subject = most_difficult_task["subject"]

    total_planned_hours = sum(t["estimated_hours"] for t in tasks)

    return {
        "subject_hours": subject_hours,
        "completed_count": len(completed),
        "pending_count": len(pending),
        "most_urgent_subject": most_urgent_subject,
        "most_difficult_subject": most_difficult_subject,
        "total_planned_hours": round(total_planned_hours, 1),
    }


def print_statistics(tasks):
    """Print the statistics report in a readable format."""
    stats = get_statistics(tasks)
    print("\n--- Study Statistics ---")

    print("Subject-wise study hours:")
    if stats["subject_hours"]:
        for subject, hours in stats["subject_hours"].items():
            print(f"  - {subject}: {hours}h")
    else:
        print("  (no tasks yet)")

    print(f"\nCompleted tasks       : {stats['completed_count']}")
    print(f"Pending tasks         : {stats['pending_count']}")
    print(f"Most urgent subject   : {stats['most_urgent_subject'] or 'N/A'}")
    print(f"Most difficult subject: {stats['most_difficult_subject'] or 'N/A'}")
    print(f"Total planned hours   : {stats['total_planned_hours']}")
