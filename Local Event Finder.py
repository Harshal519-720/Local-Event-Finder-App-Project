import tkinter as tk
import requests

# --- Setup main window
root = tk.Tk()
root.title("Local Event Finder")

# --- Input area
tk.Label(root, text="Enter City or ZIP Code:", font=("Arial", 16)).pack(pady=(10, 0))
city_entry = tk.Entry(root, font=("Arial", 14))
city_entry.pack(pady=(0, 10))

# --- Output area
results_box = tk.Text(root, height=20, width=80, font=("Arial", 12))
results_box.pack(padx=10, pady=10)
results_box.config(state=tk.DISABLED)

def get_eventbrite_events(city_name):
    results_box.config(state=tk.NORMAL)
    results_box.delete("1.0", tk.END)
    
    # Use your actual API key here
    API_KEY = "MSZSHQFXU6S14DS4D5E7"  
    
    url = "https://www.eventbriteapi.com/v3/events/search/"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    params = {
        "location.address": city_name,
        "expand": "venue",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        print(response.json())  # Debugging line to see raw response
        
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            
            if not events:
                results_box.insert(tk.END, "No events found.\n")
            else:
                for event in events[:10]:  # Show first 10 events
                    name = event.get("name", {}).get("text", "No title")
                    date = event.get("start", {}).get("local", "No date")
                    venue = event.get("venue", {})
                    venue_name = venue.get("name", "Venue not provided") if venue else "Venue not provided"
                    
                    results_box.insert(tk.END, 
                        f"Event: {name}\n"
                        f"Date: {date}\n"
                        f"Venue: {venue_name}\n"
                        "\u2014" * 40 + "\n"
                    )
        else:
            error_msg = response.json().get('error_description', 'Unknown error')
            results_box.insert(tk.END, f"Error {response.status_code}: {error_msg}\n")
    
    except Exception as e:
        results_box.insert(tk.END, f"Error: {str(e)}\n")
    
    results_box.config(state=tk.DISABLED)

def handle_search():
    city = city_entry.get().strip()
    if city:
        get_eventbrite_events(city)
    else:
        results_box.config(state=tk.NORMAL)
        results_box.delete("1.0", tk.END)
        results_box.insert(tk.END, "Please enter a city or ZIP code.\n")
        results_box.config(state=tk.DISABLED)

tk.Button(root, text="Search Events", command=handle_search, font=("Arial", 14), bg="#4CAF50", fg="white").pack(pady=(0, 15))

root.mainloop()
