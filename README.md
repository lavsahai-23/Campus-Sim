# Campus-SimSmart Study Planner
A terminal-based, personalized study schedule generator built for a
Python Essentials college course project.

Table of Contents
Project Overview
Problem Statement
Objectives
Features
Technologies Used
Python Version
Project Structure
Installation Instructions
Environment Setup
Dependencies
How to Run
How to Use the Program
Example Input/Output
Scheduling Algorithm Explained
Priority Scoring Formula
Data Storage Explanation
Limitations
Future Improvements
Project Overview
Smart Study Planner is a command-line application that helps a student
organize their study workload. The student enters their subjects/tasks
along with deadlines, estimated effort, priority, and difficulty. The
program then works out what to study and when, using a scoring
algorithm rather than a simple alphabetical or manual order, and lays
the result out as a day-by-day timetable.

Problem Statement
Students juggling multiple subjects often struggle to decide what to
study first, especially when deadlines, difficulty, and workload all
matter at the same time. Manually planning a fair, deadline-aware
study schedule is time-consuming and easy to get wrong (e.g.
forgetting an approaching deadline, or spending too long on one
subject). This project automates that decision-making process.

Objectives
Let a student record study tasks with all relevant details.
Automatically rank tasks by genuine urgency and importance, not just
the order they were entered.
Turn that ranking into a realistic, multi-day study timetable that
respects the student's available hours and days.
Warn the student about tasks that are overdue, due soon, or
unrealistic given the time left.
Track and report overall progress and study statistics.
Persist all data between runs using a simple JSON file.
Features
Student Setup — name, daily study hours, available study days, preferred session length.
Task Management — add, view, edit, delete, and mark tasks complete.
Smart Priority System — a numeric score combining deadline proximity, priority level, difficulty, and remaining workload (see Priority Scoring Formula).
Automatic Study Schedule — a day-by-day timetable generated from the priority scores.
Deadline Alerts — overdue, due tomorrow, due within 3 days, and "not enough time remaining" warnings.
Progress Tracking — totals, completion percentage, hours completed/remaining.
Study Statistics — subject-wise hours, most urgent subject, most difficult subject, and more.
JSON Data Storage — automatically created if missing; survives between runs.
Menu-Driven Interface — a numbered terminal menu for every feature.
Input Validation — the program will not crash on invalid dates, empty names, negative hours, or bad menu choices.
Technologies Used
Python 3 standard library only:

json — reading/writing the data file

os — screen clearing, file path handling

datetime — date parsing, deadline math, schedule timestamps


No external/third-party packages are used.

Python Version
Developed and tested on Python 3.10+. It should also work on any
Python 3.8+ interpreter, since it only uses standard-library features
available since early Python 3 releases.

Project Structure
smart-study-planner/
│
├── main.py           # Entry point: student setup + menu loop
├── planner.py         # Task management + priority scoring + reports
├── scheduler.py        # Day-by-day schedule generation
├── storage.py          # JSON load/save logic
├── utils.py            # Shared input-validation & display helpers
├── data/
│   └── tasks.json       # Created automatically on first run
├── README.md
└── requirements.txt      # Empty on purpose — no external packages needed
Installation Instructions
Make sure Python 3.8 or newer is installed:
python --version
Copy or download the smart-study-planner/ folder to your computer.
No pip install step is required — the project only uses the standard library.
Environment Setup
No virtual environment is strictly necessary since there are no
external dependencies, but if your course requires one:

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
Dependencies
None. requirements.txt is included (empty, with an explanatory
comment) in case your grading process expects the file to exist.

How to Run
From the smart-study-planner/ project root folder:

python main.py
On the very first run, the program will:

Create the data/ folder and data/tasks.json file automatically.
Ask you to complete the Student Setup (name, daily hours, study
days, session length).
How to Use the Program
After setup, you'll see the main menu:

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
Typical workflow:

Choose 1 to add each subject/task (deadline, hours, priority, difficulty).
Choose 6 any time to generate a fresh study schedule based on your current tasks.
Choose 7 to check for urgent deadlines.
Choose 5 as you finish tasks, to keep progress accurate.
Data auto-saves on Save Data (10) and on Exit (12) — you can also just re-run the schedule generator as your task list changes.
Example Input/Output
Adding a task:

Subject name: Calculus
Topic / task name: Differential Equations
Deadline date (YYYY-MM-DD): 2026-10-15
Estimated hours required: 4
Priority (Low/Medium/High): High
Difficulty (Easy/Medium/Hard): Hard

Task added: Calculus - Differential Equations (ID 1)
Generated schedule (example):

2026-09-25 (Friday)
--------------------
09:00-10:00 -> Physics: Electrostatics
10:15-11:15 -> Calculus: Differential Equations

2026-09-28 (Monday)
--------------------
09:00-10:00 -> Calculus: Differential Equations
10:15-11:15 -> Python: Lists and Dictionaries
Deadline alerts (example):

[OVERDUE]
  - Physics - Electrostatics (was due 2026-09-24)

[DUE WITHIN 3 DAYS]
  - Calculus - Differential Equations (due 2026-09-27)
Scheduling Algorithm Explained
scheduler.generate_schedule() builds the timetable like this:

Look at the next 14 calendar days, starting today.
Keep only the days that match the student's chosen study days (e.g. only Mon/Tue/Wed).
For each study day, repeatedly:
Recalculate every incomplete task's priority score as of that
day (so urgency naturally increases the closer a task's
deadline gets, even across the 14-day window).
Pick the single highest-scoring task that still has remaining
hours.
Allocate one "session" worth of time to it (capped by the
student's session length, the task's remaining hours, and the
hours still left in that day).
Add a 15-minute break, then continue filling the day.
Stop the whole process once every task's remaining hours reach zero, or the 14-day window runs out.
Importantly, an overdue task is never skipped — since its urgency
score is at its maximum (see below), it is simply scheduled as a
catch-up session on the very next available study day. This satisfies
the requirement that the schedule reflects a genuinely meaningful
study order, not alphabetical order or insertion order.

Schedule generation only reads task data — it does not modify your
saved hours_completed values. Only marking a task complete (menu
option 5) changes saved progress.

Priority Scoring Formula
Implemented in planner.calculate_priority_score():

score = (priority_level * 10)
      + (difficulty_level * 5)
      + urgency_score
      + remaining_hours
Factor	Values
priority_level	Low = 1, Medium = 2, High = 3
difficulty_level	Easy = 1, Medium = 2, Hard = 3
urgency_score	100 if overdue, otherwise max(0, 60 - days_left * 3)
remaining_hours	estimated_hours - hours_completed
Why this formula makes sense:

urgency_score dominates for genuinely close/overdue deadlines
(a task due tomorrow scores ~57 urgency vs. ~0 for something three
weeks away), which is why deadline-driven tasks rise to the top.
priority_level * 10 and difficulty_level * 5 let the student's
own judgment (how important/hard a task is) meaningfully shift the
ranking even between similarly-timed deadlines.
Adding remaining_hours gives a small nudge to larger tasks, since
they need to be started earlier to finish on time.
Completed tasks always score 0 so they never appear in the
schedule or in "most urgent" statistics.
This produces a genuinely different order than simply sorting by
deadline or by priority alone — try adding a Low-priority task due
tomorrow next to a High-priority task due in three days and compare
their scores.

Data Storage Explanation
All data is stored in a single JSON file at data/tasks.json,
structured as:

{
    "student": {
        "name": "...",
        "daily_hours": 3.0,
        "study_days": ["Monday", "Wednesday", "Friday"],
        "session_length": 1.0
    },
    "tasks": [
        {
            "id": 1,
            "subject": "Calculus",
            "topic": "Differential Equations",
            "deadline": "2026-10-15",
            "estimated_hours": 4.0,
            "hours_completed": 0.0,
            "priority": "High",
            "difficulty": "Hard",
            "completed": false
        }
    ]
}
storage.ensure_data_file() creates the data/ folder and file
automatically if they don't exist, so the program can start from a
completely empty project.
storage.load_data() reads and parses the JSON; if the file is
missing, empty, or corrupted, it safely falls back to a blank
default structure instead of crashing.
storage.save_data() writes the current in-memory student info and
task list back to disk, called from the "Save Data" menu option and
automatically on Exit.
Limitations
The scheduler only looks 14 days ahead; tasks with deadlines beyond
that window will still be scored correctly but may not receive
scheduled sessions until later runs.
The schedule always starts each day at a fixed 09:00 — it doesn't
account for the student's other commitments during the day.
There is no reminder/notification system outside of the in-app
Deadline Alerts menu option (no email, SMS, or OS notifications).
Only one student's data is stored per tasks.json file (no
multi-user support).
The "realistic hours available" estimate in deadline alerts assumes
a roughly even weekly rhythm and doesn't account for weeks with
holidays or exceptions.
Future Improvements
Allow tasks to be broken into sub-topics with independent hour
estimates.
Let the student customize the schedule's daily start time.
Add recurring tasks (e.g. weekly revision sessions).
Export the generated schedule to a calendar file (.ics) or PDF.
Add a "snooze"/reschedule option directly from the Deadline Alerts
screen.
Support multiple student profiles in one data file.
Project Report Support
Abstract
Smart Study Planner is a command-line Python application that helps
students plan study time across multiple subjects by automatically
prioritizing tasks and generating a day-by-day schedule, rather than
requiring the student to manually decide what to study and when.

Problem Statement
See Problem Statement above.

Objectives
See Objectives above.

Methodology
The program collects structured task data from the student (subject,
topic, deadline, estimated hours, priority, difficulty) and stores it
in JSON. A scoring function combines deadline urgency, stated
priority, difficulty, and remaining workload into a single comparable
number per task. A greedy, day-by-day allocation algorithm then
consumes tasks in descending score order to build a realistic
timetable constrained by the student's available hours and days.

Algorithm
See Scheduling Algorithm Explained
and Priority Scoring Formula above.

Features
See Features above.

Python Concepts Used
Variables and basic data types (str, float, int, bool)
Input/output via input()/print()
Conditionals (if/elif/else)
for loops (iterating tasks) and while loops (menu loop, input
validation, day-filling logic)
Functions with parameters, return values, and default arguments
Lists (tasks, study_days, schedule sessions)
Tuples (each scheduled session is stored as a tuple of
(start, end, subject, topic))
Sets (set(student["study_days"]), deduplicating chosen study days)
Dictionaries (each task, the student profile, subject_hours stats,
the JSON structure itself)
String formatting/operations (.format(), f-strings, .title(),
.strip(), slicing for column widths)
File handling and JSON (storage.py)
Exception handling (try/except around json.load,
datetime.strptime, float() conversions)
Modules (the project is split into 5 cooperating modules, plus the
standard-library json, os, and datetime modules)
Date/time handling (datetime.date, timedelta, deadline math)
Testing Cases
The following were manually and programmatically tested during
development (you should re-verify these yourself — see the Student
Understanding Checklist):

Adding a task with valid data → appears correctly in "View Tasks".
Entering an invalid date (e.g. 2026-13-40) → re-prompts instead of crashing.
Entering a negative or non-numeric value for hours → re-prompts.
Entering an empty subject name → re-prompts.
Choosing an invalid menu option (e.g. 99 or abc) → re-prompts.
Editing a task and leaving fields blank → original values are kept.
Deleting a task by ID that doesn't exist → shows an error, no crash.
Marking a task complete → excluded from future schedules and "most urgent" stats.
An overdue task → appears in [OVERDUE] alerts and is still scheduled as a catch-up session (not silently dropped).
A corrupted tasks.json file → the program recovers with a warning instead of crashing.
Zero daily study hours or no study days set → schedule generation reports it cannot build a schedule, instead of crashing.
Running the program with an empty task list → all reports handle the "0 tasks" case gracefully (no division-by-zero, etc.).
Expected Results
A student who enters their real subjects and deadlines should see a
sensibly ordered, multi-day study plan where urgent and overdue tasks
consistently appear before low-urgency tasks, progress and statistics
accurately reflect completed vs. pending work, and their data persists
correctly the next time they run the program.

Limitations
See Limitations above.

Future Scope
See Future Improvements above.

Conclusion
Smart Study Planner demonstrates how a small set of well-organized
Python modules — input validation, JSON persistence, a scoring
algorithm, and a greedy scheduler — can be combined into a genuinely
useful command-line tool, while staying simple enough for a first-year
CSE student to read, understand, and extend.