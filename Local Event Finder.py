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

            event_list.append(f"\u2728 {name}\n\U0001F3AD Venue: {venue}\n\U0001F4C5 Date: {date}\n\u23F0 Time: {time}\n{'-'*40}")
        return event_list

    except Exception as e:
        return [f"Error: {e}"]


root = tk.Tk()
root.title("Eventure")
root.geometry("720x620")
root.configure(bg="#f7f9fc")

# Fonts and Styles
title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
label_font = tkfont.Font(family="Helvetica", size=12)
button_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
result_font = tkfont.Font(family="Segoe UI", size=10)

# Title Label
title_label = tk.Label(root, text="Eventure", font=title_font, fg="#3f51b5", bg="#f7f9fc", anchor="w")
title_label.pack(anchor="nw", padx=20, pady=(10, 0))

# Input Label and Entry
label = tk.Label(root, text="Enter City:", font=label_font, bg="#f7f9fc")
label.pack(pady=(20, 5))

city_entry = tk.Entry(root, font=label_font, width=40, bd=2, relief="groove", highlightbackground="#cccccc")
city_entry.pack(pady=5)

# Output Text Box Frame with Border
output_frame = tk.Frame(root, bg="#ffffff", bd=1, relief="solid")
output_frame.pack(pady=10, padx=20, fill="both", expand=True)

output = tk.Text(output_frame, height=20, width=80, font=result_font, bg="#ffffff", fg="#2e2e2e",
                 wrap="word", bd=0, padx=10, pady=10)
output.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(output_frame, command=output.yview)
scrollbar.pack(side="right", fill="y")
output.config(yscrollcommand=scrollbar.set)

def on_search_click():
    city = city_entry.get()
    results = fetch_live_events(city)

    output.delete("1.0", tk.END)

    if results:
        for line in results:
            output.insert(tk.END, line + "\n")
    else:
        output.insert(tk.END, "\u26A0\ufe0f No events found.")

# Search Button
search_button = tk.Button(root, text="Search Events", command=on_search_click,
                          bg="#3f51b5", fg="white", font=button_font, padx=10, pady=6,
                          activebackground="#303f9f", activeforeground="white",
                          bd=0, relief="flat", cursor="hand2")
search_button.pack(pady=10)


root.mainloop()
