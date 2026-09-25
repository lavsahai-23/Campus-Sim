"""
scheduler.py
------------
Generates a day-by-day study schedule from the current task list,
using the priority scores from planner.py.

ALGORITHM OVERVIEW
-------------------
1. Look at the next 14 calendar days starting today.
2. Keep only the days that match the student's chosen study days
   (e.g. only Monday/Tuesday/Wednesday).
3. For each study day, keep filling the day's available hours by
   repeatedly picking the *highest-scoring eligible task*:
       - not completed
       - still has remaining hours to study
       - deadline has not already passed by that day
   and carving off one "session" worth of time from it (or less,
   if that's all that's left in the day or in the task).
4. A 15-minute gap is left between consecutive sessions on the same
   day, similar to a real study timetable.
5. Scores are recalculated fresh each time a task is picked, using a
   *working copy* of remaining hours -- so generating a schedule never
   changes the actual saved task data. The student has to explicitly
   mark a task complete for that to happen.

This is a straightforward greedy algorithm (not a complex optimizer),
which keeps it understandable while still producing a sensible,
priority-driven, multi-day plan instead of dumping everything on
day one.
"""

from datetime import datetime, timedelta, time as dtime

from planner import calculate_priority_score
from utils import days_between

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SCHEDULE_START_HOUR = 9  # Schedules start at 09:00 by default.
BREAK_MINUTES = 15
LOOKAHEAD_DAYS = 14


def generate_schedule(tasks, student, reference_date=None):
    """
    Build and return a schedule as a dictionary:
        { "2026-10-01 (Wednesday)": [ (start_str, end_str, subject, topic), ... ], ... }

    Only days with at least one scheduled session are included.
    """
    if reference_date is None:
        from utils import today
        reference_date = today()

    study_days = set(student.get("study_days", []))
    daily_hours = student.get("daily_hours", 0)
    session_length = student.get("session_length", 1.0)

    if daily_hours <= 0 or session_length <= 0 or not study_days:
        return {}

    # Working copy: remaining hours per task ID, so we never mutate the
    # real saved data just by generating a preview schedule.
    remaining_hours = {
        t["id"]: max(0.0, t["estimated_hours"] - t["hours_completed"])
        for t in tasks
        if not t["completed"]
    }

    schedule = {}

    for day_offset in range(LOOKAHEAD_DAYS):
        current_date = reference_date + timedelta(days=day_offset)
        weekday_name = DAY_NAMES[current_date.weekday()]

        if weekday_name not in study_days:
            continue

        # Stop once every task has been fully scheduled.
        if all(hours <= 0 for hours in remaining_hours.values()):
            break

        day_sessions = _schedule_one_day(
            tasks, remaining_hours, current_date, daily_hours, session_length
        )

        if day_sessions:
            label = f"{current_date.isoformat()} ({weekday_name})"
            schedule[label] = day_sessions

    return schedule


def _schedule_one_day(tasks, remaining_hours, current_date, daily_hours, session_length):
    """
    Fill a single day's worth of sessions using a greedy, priority-first
    approach. Returns a list of (start_time, end_time, subject, topic) tuples.
    """
    sessions = []
    hours_used = 0.0
    clock = datetime.combine(current_date, dtime(hour=SCHEDULE_START_HOUR))

    while hours_used < daily_hours:
        eligible_task = _pick_next_task(tasks, remaining_hours, current_date)
        if eligible_task is None:
            break  # nothing left that is eligible for this day

        time_left_today = daily_hours - hours_used
        allocation = min(session_length, remaining_hours[eligible_task["id"]], time_left_today)
        if allocation <= 0:
            break

        start_time = clock
        end_time = clock + timedelta(hours=allocation)
        sessions.append((
            start_time.strftime("%H:%M"),
            end_time.strftime("%H:%M"),
            eligible_task["subject"],
            eligible_task["topic"],
        ))

        remaining_hours[eligible_task["id"]] -= allocation
        hours_used += allocation
        clock = end_time + timedelta(minutes=BREAK_MINUTES)

    return sessions


def _pick_next_task(tasks, remaining_hours, current_date):
    """
    Among all tasks that still have remaining hours, return the one with
    the highest priority score, recalculated relative to current_date so
    scores shift appropriately for later days in the schedule.

    Note: a task is NOT excluded just because current_date is past its
    deadline. An overdue task still needs to be studied -- it should be
    scheduled as a catch-up session, and its urgency_score (see
    planner.calculate_priority_score) already makes sure it is picked
    ahead of everything else.
    """
    best_task = None
    best_score = -1

    for task in tasks:
        if task["completed"]:
            continue
        if remaining_hours.get(task["id"], 0) <= 0:
            continue

        score = calculate_priority_score(task, reference_date=current_date)
        if score > best_score:
            best_score = score
            best_task = task

    return best_task


def print_schedule(schedule):
    """Print a generated schedule in a clean, readable format."""
    if not schedule:
        print("\nNo schedule could be generated. Make sure you have:")
        print("  - at least one incomplete task")
        print("  - study days and daily hours set up")
        return

    for day_label, sessions in schedule.items():
        print(f"\n{day_label}")
        print("-" * len(day_label))
        for start, end, subject, topic in sessions:
            print(f"{start}-{end} -> {subject}: {topic}")
