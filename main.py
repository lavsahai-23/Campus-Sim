"""
main.py
-------
Entry point for the Smart Study Planner.

Run this file from the project root with:
    python main.py

This module is intentionally kept "thin": it handles the student setup
flow and the terminal menu loop, and delegates all the real work to
planner.py (task management + priority scoring), scheduler.py
(schedule generation), and storage.py (saving/loading JSON data).
"""

from utils import (
    clear_screen,
    print_header,
    pause,
    get_non_empty_string,
    get_positive_float,
    get_menu_choice,
    get_yes_no,
)
from storage import load_data, save_data
import planner
import scheduler

VALID_STUDY_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

MENU_TEXT = """
===== SMART STUDY PLANNER =====

1. Add Study Task
2. View Tasks
3. Edit Task
4. Delete Task
5. Mark Task Complete
6. Generate Study Schedule
7. View Deadline Alerts
8. View Progress
9. View Statistics
10. Save Data
11. Update Student Setup
12. Exit
"""


def setup_student(student, is_first_run):
    """
    Ask the student for their name, daily study hours, available study
    days, and preferred session length. If a name already exists
    (returning user), offer to skip re-entering everything.
    """
    print_header("STUDENT SETUP")

    if not is_first_run:
        print(f"Current setup for {student['name']}:")
        print(f"  Daily study hours : {student['daily_hours']}")
        print(f"  Study days        : {', '.join(student['study_days'])}")
        print(f"  Session length    : {student['session_length']} hour(s)")
        if not get_yes_no("Do you want to update this setup?"):
            return student

    student["name"] = get_non_empty_string("Enter your name: ")
    student["daily_hours"] = get_positive_float("How many hours can you study per day? ")

    print(f"Choose your available study days from: {', '.join(VALID_STUDY_DAYS)}")
    print("Enter them separated by commas (e.g. Monday, Wednesday, Friday):")
    while True:
        raw = input("> ").strip()
        chosen = [d.strip().title() for d in raw.split(",") if d.strip()]
        valid = [d for d in chosen if d in VALID_STUDY_DAYS]
        if valid:
            student["study_days"] = sorted(set(valid), key=VALID_STUDY_DAYS.index)
            break
        print("Please enter at least one valid day name.")

    student["session_length"] = get_positive_float(
        "Preferred study session length in hours (e.g. 1 or 1.5): "
    )

    print("\nSetup saved!")
    return student


def main():
    data = load_data()
    student = data["student"]
    tasks = data["tasks"]

    is_first_run = not student.get("name")
    if is_first_run:
        print_header("WELCOME TO THE SMART STUDY PLANNER")
        student = setup_student(student, is_first_run=True)
        data["student"] = student
        save_data(data)

    valid_choices = [str(n) for n in range(1, 13)]

    while True:
        clear_screen()
        print(f"Welcome, {student['name']}!")
        print(MENU_TEXT)
        choice = get_menu_choice("Choose an option (1-12): ", valid_choices)

        if choice == "1":
            print_header("ADD STUDY TASK")
            planner.add_task(tasks)

        elif choice == "2":
            print_header("ALL TASKS")
            planner.view_tasks(tasks)

        elif choice == "3":
            print_header("EDIT TASK")
            planner.edit_task(tasks)

        elif choice == "4":
            print_header("DELETE TASK")
            planner.delete_task(tasks)

        elif choice == "5":
            print_header("MARK TASK COMPLETE")
            planner.mark_task_complete(tasks)

        elif choice == "6":
            print_header("STUDY SCHEDULE")
            schedule = scheduler.generate_schedule(tasks, student)
            scheduler.print_schedule(schedule)

        elif choice == "7":
            print_header("DEADLINE ALERTS")
            planner.check_deadline_alerts(tasks, student)

        elif choice == "8":
            print_header("PROGRESS")
            planner.print_progress_report(tasks)

        elif choice == "9":
            print_header("STATISTICS")
            planner.print_statistics(tasks)

        elif choice == "10":
            data["student"] = student
            data["tasks"] = tasks
            save_data(data)
            print("\nData saved successfully.")

        elif choice == "11":
            student = setup_student(student, is_first_run=False)
            data["student"] = student

        elif choice == "12":
            data["student"] = student
            data["tasks"] = tasks
            save_data(data)
            print("\nData saved. Goodbye, and good luck studying!")
            break

        pause()


if __name__ == "__main__":
    main()
