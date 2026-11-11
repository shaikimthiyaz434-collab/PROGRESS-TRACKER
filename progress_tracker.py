"""
PROGRESS TRACKER
A simple command-line application to track study subjects and daily progress.

Features:
- Add a subject and record what you studied
- View all progress entries
- Search entries by subject
- Update an entry
- Delete an entry
- Save data automatically in progress_data.json

How to run:
1. Install Python 3 (no extra packages are required).
2. Save this file as progress_tracker.py.
3. Open a terminal in the same folder.
4. Run: python progress_tracker.py

The JSON data file is created automatically in the same folder.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("progress_data.json")
DATE_FORMAT = "%Y-%m-%d"


def load_data():
    """Load saved progress entries from the JSON file."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read the data file. Starting with an empty list.")
        return []


def save_data(entries):
    """Save all progress entries to the JSON file."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(entries, file, indent=4, ensure_ascii=False)
    except OSError as error:
        print(f"Error saving data: {error}")


def get_date():
    """Ask for a date and validate it. Blank input means today's date."""
    while True:
        value = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not value:
            return datetime.today().strftime(DATE_FORMAT)

        try:
            return datetime.strptime(value, DATE_FORMAT).strftime(DATE_FORMAT)
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD, for example 2026-11-10.")


def add_entry(entries):
    """Add a new study progress entry."""
    print("\n--- Add Progress ---")
    subject = input("Subject name: ").strip()
    if not subject:
        print("Subject name cannot be empty.")
        return

    topic = input("What did you study? ").strip()
    if not topic:
        print("Topic/details cannot be empty.")
        return

    study_date = get_date()
    try:
        minutes_text = input("Study time in minutes (optional, press Enter to skip): ").strip()
        minutes = int(minutes_text) if minutes_text else 0
        if minutes < 0:
            raise ValueError
    except ValueError:
        print("Please enter a valid non-negative number of minutes.")
        return

    entry = {
        "id": max((item.get("id", 0) for item in entries), default=0) + 1,
        "subject": subject,
        "topic": topic,
        "date": study_date,
        "minutes": minutes,
        "completed": False
    }

    entries.append(entry)
    save_data(entries)
    print("Progress added successfully!")


def display_entries(entries):
    """Display progress entries in a readable format."""
    if not entries:
        print("\nNo progress entries found.")
        return

    print("\n" + "=" * 72)
    print(f"{'ID':<5} {'DATE':<12} {'SUBJECT':<18} {'MIN':<6} {'STATUS':<10} TOPIC")
    print("-" * 72)

    for entry in sorted(entries, key=lambda item: (item.get("date", ""), item.get("id", 0))):
        status = "Completed" if entry.get("completed", False) else "In progress"
        topic = entry.get("topic", "")
        if len(topic) > 28:
            topic = topic[:25] + "..."
        print(
            f"{entry.get('id', '-'):<5} "
            f"{entry.get('date', '-'):<12} "
            f"{entry.get('subject', '-')[:17]:<18} "
            f"{entry.get('minutes', 0):<6} "
            f"{status:<10} {topic}"
        )

    print("=" * 72)


def find_entry(entries, entry_id):
    """Return an entry matching the given ID, or None."""
    for entry in entries:
        if entry.get("id") == entry_id:
            return entry
    return None


def ask_for_id():
    """Read and validate an entry ID."""
    try:
        return int(input("Enter entry ID: ").strip())
    except ValueError:
        print("Please enter a valid numeric ID.")
        return None


def search_entries(entries):
    """Search entries by subject name."""
    print("\n--- Search by Subject ---")
    keyword = input("Enter subject name or part of it: ").strip().lower()
    if not keyword:
        print("Search text cannot be empty.")
        return

    matches = [
        entry for entry in entries
        if keyword in entry.get("subject", "").lower()
    ]
    display_entries(matches)


def update_entry(entries):
    """Update the subject, topic, date, study time, or completion status."""
    print("\n--- Update Progress ---")
    entry_id = ask_for_id()
    if entry_id is None:
        return

    entry = find_entry(entries, entry_id)
    if entry is None:
        print("Entry not found.")
        return

    print("Press Enter to keep the current value.")
    subject = input(f"Subject [{entry['subject']}]: ").strip()
    topic = input(f"Topic/details [{entry['topic']}]: ").strip()
    date_value = input(f"Date [{entry['date']}] (YYYY-MM-DD): ").strip()
    minutes_value = input(f"Study minutes [{entry.get('minutes', 0)}]: ").strip()

    if subject:
        entry["subject"] = subject
    if topic:
        entry["topic"] = topic

    if date_value:
        try:
            entry["date"] = datetime.strptime(date_value, DATE_FORMAT).strftime(DATE_FORMAT)
        except ValueError:
            print("Invalid date. Date was not changed.")

    if minutes_value:
        try:
            minutes = int(minutes_value)
            if minutes < 0:
                raise ValueError
            entry["minutes"] = minutes
        except ValueError:
            print("Invalid study time. Study time was not changed.")

    status_value = input(
        f"Completed? (y/n, blank to keep {'yes' if entry.get('completed', False) else 'no'}): "
    ).strip().lower()
    if status_value == "y":
        entry["completed"] = True
    elif status_value == "n":
        entry["completed"] = False

    save_data(entries)
    print("Entry updated successfully.")


def delete_entry(entries):
    """Delete an entry after confirmation."""
    print("\n--- Delete Progress ---")
    entry_id = ask_for_id()
    if entry_id is None:
        return

    entry = find_entry(entries, entry_id)
    if entry is None:
        print("Entry not found.")
        return

    print(f"Subject: {entry['subject']} | Topic: {entry['topic']}")
    confirm = input("Are you sure you want to delete this entry? (y/n): ").strip().lower()
    if confirm == "y":
        entries.remove(entry)
        save_data(entries)
        print("Entry deleted.")
    else:
        print("Delete cancelled.")


def show_summary(entries):
    """Show a small summary of tracked study time and subjects."""
    total_entries = len(entries)
    total_minutes = sum(entry.get("minutes", 0) for entry in entries)
    completed = sum(1 for entry in entries if entry.get("completed", False))
    subjects = sorted({entry.get("subject", "") for entry in entries if entry.get("subject")})

    print("\n--- Progress Summary ---")
    print(f"Total entries: {total_entries}")
    print(f"Subjects tracked: {len(subjects)}")
    print(f"Total study time: {total_minutes} minutes ({total_minutes / 60:.1f} hours)")
    print(f"Completed entries: {completed}")
    if subjects:
        print("Subjects: " + ", ".join(subjects))


def main():
    """Run the application menu."""
    entries = load_data()

    while True:
        print("\n========== PROGRESS TRACKER ==========")
        print("1. Add progress")
        print("2. View all progress")
        print("3. Search by subject")
        print("4. Update an entry")
        print("5. Delete an entry")
        print("6. View summary")
        print("7. Exit")

        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            add_entry(entries)
        elif choice == "2":
            display_entries(entries)
        elif choice == "3":
            search_entries(entries)
        elif choice == "4":
            update_entry(entries)
        elif choice == "5":
            delete_entry(entries)
        elif choice == "6":
            show_summary(entries)
        elif choice == "7":
            print("Your progress is saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 7.")


if __name__ == "__main__":
    main()
