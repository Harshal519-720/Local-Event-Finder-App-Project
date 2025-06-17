import tkinter as tk
from tkinter import font as tkfont
import requests
from colorama import init
from datetime import datetime

init(autoreset=True)

light_theme = {
    "bg": "#f7f9fc",
    "fg": "#2e2e2e",
    "entry_bg": "#ffffff",
    "button_bg": "#3f51b5",
    "button_fg": "white",
    "text_bg": "#ffffff",
    "text_fg": "#2e2e2e"
}

dark_theme = {
    "bg": "#1e1e1e",
    "fg": "#e0e0e0",
    "entry_bg": "#333333",
    "button_bg": "#5c6bc0",
    "button_fg": "white",
    "text_bg": "#2a2a2a",
    "text_fg": "#f0f0f0"
}

current_theme = "light"

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
                time_obj = datetime.strptime(raw_time, "%H:%M:%S") if len(raw_time) > 5 else datetime.strptime(raw_time, "%H:%M")
                time = time_obj.strftime("%I:%M %p")
            except:
                time = raw_time

            event_list.append(f"\u2728 {name}\n\U0001F3AD Venue: {venue}\n\U0001F4C5 Date: {date}\n\u23F0 Time: {time}\n{'-'*40}")
        return event_list

    except Exception as e:
        return [f"Error: {e}"]

root = tk.Tk()
root.title("Eventure")
root.geometry("720x660")

title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
label_font = tkfont.Font(family="Helvetica", size=12)
button_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
result_font = tkfont.Font(family="Segoe UI", size=10)

title_label = tk.Label(root, text="Eventure", font=title_font, anchor="w")
title_label.pack(anchor="nw", padx=20, pady=(10, 0))

label = tk.Label(root, text="Enter City:", font=label_font)
label.pack(pady=(20, 5))

city_entry = tk.Entry(root, font=label_font, width=40, bd=2, relief="groove", highlightbackground="#cccccc")
city_entry.pack(pady=5)

output_frame = tk.Frame(root, bd=1, relief="solid")
output_frame.pack(pady=10, padx=20, fill="both", expand=True)

output = tk.Text(output_frame, height=20, width=80, font=result_font, wrap="word", bd=0, padx=10, pady=10)
output.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(output_frame, command=output.yview)
scrollbar.pack(side="right", fill="y")
output.config(yscrollcommand=scrollbar.set)

def apply_theme(theme):
    root.config(bg=theme["bg"])
    title_label.config(bg=theme["bg"], fg=theme["fg"])
    label.config(bg=theme["bg"], fg=theme["fg"])
    city_entry.config(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
    output.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["text_fg"])
    output_frame.config(bg=theme["bg"])
    search_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"], activeforeground=theme["button_fg"])
    theme_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"], activeforeground=theme["button_fg"])

def switch_theme():
    global current_theme
    if current_theme == "light":
        apply_theme(dark_theme)
        current_theme = "dark"
    else:
        apply_theme(light_theme)
        current_theme = "light"

def on_search_click():
    city = city_entry.get()
    results = fetch_live_events(city)
    output.delete("1.0", tk.END)
    if results:
        for line in results:
            output.insert(tk.END, line + "\n")
    else:
        output.insert(tk.END, "\u26A0\ufe0f No events found.")

search_button = tk.Button(root, text="Search Events", command=on_search_click, font=button_font, padx=10, pady=6, bd=0, relief="flat", cursor="hand2")
search_button.pack(pady=5)

theme_button = tk.Button(root, text="✨ Switch Theme", command=switch_theme, font=button_font, padx=10, pady=6, bd=0, relief="flat", cursor="hand2")
theme_button.pack(pady=5)

apply_theme(light_theme)

root.mainloop()
