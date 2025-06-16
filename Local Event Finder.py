import tkinter as tk
from tkinter import font as tkfont
import requests
from colorama import init
from datetime import datetime

init(autoreset=True)


def fetch_live_events(city):
    API_KEY = "qGDnOricwKqTRb66e5xyDWPYOWsQGDCT"  
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={API_KEY}&city={city}&size=5"

    try:
        response = requests.get(url)
        data = response.json()
        events = data["_embedded"]["events"]

        event_list = []
        for e in events:
            name = e.get("name", "N/A")
            raw_date = e["dates"]["start"].get("localDate", "Unknown")
            raw_time = e["dates"]["start"].get("localTime", "Unknown")
            venue = e["_embedded"]["venues"][0].get("name", "Unknown Venue")

            try:
                date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%B %d, %Y")
            except:
                date = raw_date

            try:
                time = datetime.strptime(raw_time, "%H:%M").strftime("%I:%M %p")
            except:
                time = raw_time

            event_list.append(f"{name} at {venue} on {date} at {time}")
        return event_list

    except Exception as e:
        return [f"Error: {e}"]


root = tk.Tk()
root.title("Eventure")
root.geometry("700x600")
root.configure(bg="#f0f0f5")

# Fonts and Styles
title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
label_font = tkfont.Font(family="Helvetica", size=12)
button_font = tkfont.Font(family="Helvetica", size=10, weight="bold")

# Title Label
title_label = tk.Label(root, text="Eventure", font=title_font, fg="#4B9CD3", bg="#f0f0f5", anchor="w")
title_label.pack(anchor="nw", padx=20, pady=(10, 0))

# Input Label and Entry
label = tk.Label(root, text="Enter City:", font=label_font, bg="#f0f0f5")
label.pack(pady=(20, 5))

city_entry = tk.Entry(root, font=label_font, width=40)
city_entry.pack(pady=5)

# Output Text Box
output = tk.Text(root, height=20, width=80, font=("Courier New", 10), bg="#ffffff", fg="#333333", wrap="word")
output.pack(pady=10, padx=20)

def on_search_click():
    city = city_entry.get()
    results = fetch_live_events(city)

    output.delete("1.0", tk.END)  

    if results:
        for line in results:
            output.insert(tk.END, line + "\n\n")
    else:
        output.insert(tk.END, "No events found.")

# Search Button
search_button = tk.Button(root, text="Search Events", command=on_search_click,
                          bg="#4B9CD3", fg="white", font=button_font, padx=10, pady=5,
                          activebackground="#357ABD", activeforeground="white",
                          bd=0, relief="flat")
search_button.pack(pady=5)


root.mainloop()
