import json            
from datetime import datetime  
import os              
from tabulate import tabulate  
from colorama import Fore, Style, init  
init(autoreset=True)  


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





