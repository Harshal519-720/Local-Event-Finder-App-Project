import json
from datetime import datetime
import os
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

# ------------------------------
# Event Class
# ------------------------------
class Event:
    def __init__(self, title, date_str, time_str, description):
        self.title = title
        self.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        self.time = datetime.strptime(time_str, "%H:%M").time()
        self.description = description

    def to_dict(self):
        return {
            "title": self.title,
            "date": self.date.strftime("%Y-%m-%d"),
            "time": self.time.strftime("%H:%M"),
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            date_str=data["date"],
            time_str=data["time"],
            description=data["description"]
        )

    def __str__(self):
        return f"{self.title} on {self.date} at {self.time} - {self.description}"

# ------------------------------
# Helper Functions
# ------------------------------

def save_events(events, filename):
    data = [event.to_dict() for event in events]
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_events(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        data = json.load(f)
        return [Event.from_dict(item) for item in data]

def view_all_events(events):
    sorted_events = sorted(events, key=lambda e: e.title)
    for event in sorted_events:
        print(f"{event.title} on {event.date} at {event.time}")

def view_recent_events(events, year):
    recent = [e for e in events if e.date.year >= year]
    for event in recent:
        print(f"{event.title} ({event.date.year})")

def search_events(events, keyword):
    keyword = keyword.lower()
    matches = [e for e in events if keyword in e.title.lower() or keyword in e.description.lower()]
    return matches

def search_by_year(events, year_input):
    try:
        year = int(year_input)
        return [e for e in events if e.date.year == year]
    except ValueError:
        print("Invalid year.")
        return []

# ------------------------------
# Main Menu
# ------------------------------

def main():
    events = load_events("events.json")  # Load from file at start

    while True:
        print(Fore.CYAN + "\n--- Local Event Finder ---")
        print("1. Add Event")
        print("2. View All Events")
        print("3. View Upcoming Events")
        print("4. Search by Keyword")
        print("5. Search by Year")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            title = input("Enter title: ")
            date_str = input("Enter date (YYYY-MM-DD): ")
            time_str = input("Enter time (HH:MM): ")
            description = input("Enter description: ")
            try:
                event = Event(title, date_str, time_str, description)
                events.append(event)
                print(Fore.GREEN + "Event added successfully!")
            except Exception as e:
                print(Fore.RED + f"Error adding event: {e}")

        elif choice == "2":
            view_all_events(events)

        elif choice == "3":
            year = datetime.now().year
            view_recent_events(events, year)

        elif choice == "4":
            keyword = input("Enter keyword: ")
            matches = search_events(events, keyword)
            for event in matches:
                print(f"{event.title} on {event.date} at {event.time}")

        elif choice == "5":
            year_input = input("Enter year: ")
            matches = search_by_year(events, year_input)
            for event in matches:
                print(f"{event.title} on {event.date} at {event.time}")

        elif choice == "6":
            save_events(events, "events.json")
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")

# ------------------------------
# Run the App
# ------------------------------
if __name__ == "__main__":
    main()
