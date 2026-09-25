"""
storage.py
----------
Handles all reading and writing of the program's JSON data file.

The data file stores a single JSON object shaped like this:

{
    "student": {
        "name": "Lav",
        "daily_hours": 3.0,
        "study_days": ["Monday", "Tuesday", "Wednesday"],
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
        },
        ...
    ]
}

Keeping storage logic in its own module means the rest of the program
never has to know *how* data is saved -- it just calls load_data()
and save_data().
"""

import json
import os

# The data file lives in the "data" folder next to this script, no matter
# which directory the user runs "python main.py" from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")

# The structure used when no data file exists yet (a brand new install).
DEFAULT_DATA = {
    "student": {
        "name": "",
        "daily_hours": 2.0,
        "study_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "session_length": 1.0,
    },
    "tasks": [],
}


def ensure_data_file():
    """
    Make sure the data folder and JSON file exist. If they don't,
    create them with default/empty content. This means the program
    can start from a completely empty project folder.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, indent=4)


def load_data():
    """
    Load the student info + task list from the JSON file.
    If the file is missing or corrupted, fall back to default data
    instead of crashing the whole program.
    """
    ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Basic structure check in case the file was hand-edited badly.
            if "student" not in data or "tasks" not in data:
                raise ValueError("Data file is missing required keys.")
            return data
    except (json.JSONDecodeError, ValueError):
        print("Warning: data file was unreadable or corrupted. Starting fresh.")
        return json.loads(json.dumps(DEFAULT_DATA))  # deep copy


def save_data(data):
    """Save the given data dictionary (student + tasks) back to the JSON file."""
    ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_next_task_id(tasks):
    """
    Work out the next unused task ID. IDs are simple incrementing
    integers, which makes editing/deleting a specific task easy.
    """
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1
