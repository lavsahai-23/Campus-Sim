"""
utils.py
--------
Small, reusable helper functions used across the Smart Study Planner:
- printing/formatting helpers
- input validation loops (so main.py / planner.py don't repeat
  the same "keep asking until the input is valid" logic everywhere)

Keeping these in one module demonstrates good code organization
and keeps the same validation rules consistent across the whole program.
"""

import os
from datetime import datetime, date


def clear_screen():
    """Clear the terminal screen on both Windows and Unix-like systems."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title):
    """Print a consistent, readable section header."""
    print("\n" + "=" * 50)
    print(title.center(50))
    print("=" * 50)


def pause():
    """Pause execution until the user presses Enter, so they can read output."""
    input("\nPress Enter to continue...")


def get_non_empty_string(prompt):
    """
    Keep asking until the user types something that is not just
    whitespace. Prevents empty subject/topic names.
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_positive_float(prompt, allow_zero=False):
    """
    Ask for a number (hours, etc.) and keep re-prompting until the
    user enters a valid, non-negative number.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("Please enter a valid number (e.g. 2 or 2.5).")
            continue

        if allow_zero and value < 0:
            print("Please enter a number that is 0 or greater.")
        elif not allow_zero and value <= 0:
            print("Please enter a number greater than 0.")
        else:
            return value


def get_positive_int(prompt):
    """Ask for a whole number greater than 0 (used for menu choices, etc.)."""
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("Please enter a valid positive whole number.")


def get_valid_date(prompt):
    """
    Ask for a date in YYYY-MM-DD format and keep re-prompting until
    it is a real, valid calendar date. Returns a datetime.date object.
    """
    while True:
        raw = input(prompt + " (YYYY-MM-DD): ").strip()
        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d").date()
            return parsed
        except ValueError:
            print("That doesn't look like a valid date. Example: 2026-10-15")


def get_choice_from_list(prompt, options):
    """
    Ask the user to choose one option from a list of allowed strings
    (case-insensitive). Used for Priority (Low/Medium/High) and
    Difficulty (Easy/Medium/Hard).
    Returns the option in its original (properly-capitalized) form.
    """
    options_display = "/".join(options)
    while True:
        raw = input(f"{prompt} ({options_display}): ").strip().lower()
        for option in options:
            if raw == option.lower():
                return option
        print(f"Invalid choice. Please choose one of: {options_display}")


def get_yes_no(prompt):
    """Ask a yes/no question and return True/False."""
    while True:
        raw = input(prompt + " (y/n): ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer with 'y' or 'n'.")


def get_menu_choice(prompt, valid_choices):
    """
    Ask for a menu option and validate it against a set/list of
    valid string choices (e.g. "1".."11"). Prevents crashes on
    non-numeric or out-of-range menu input.
    """
    while True:
        raw = input(prompt).strip()
        if raw in valid_choices:
            return raw
        print("Invalid menu choice. Please try again.")


def days_between(today, target_date):
    """Return the number of days between today and target_date (can be negative)."""
    return (target_date - today).days


def today():
    """Return today's date. Centralized here so it's easy to reason about/test."""
    return date.today()
