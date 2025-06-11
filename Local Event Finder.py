
import tkinter as tk
import requests


root = tk.Tk()
root.title("Local Event Finder")


city_label = tk.Label(root, text="Enter City/Zip Code:", font=("Poppins", 16))
city_label.pack()


city_entry = tk.Entry(root)
city_entry.pack()


results_box = tk.Text(root, height=20, width=80, font=("Poppins", 12))
results_box.pack(pady=10)
results_box.delete("1.0", tk.END)

def get_eventbrite_events(city_name):
    url = "https://www.eventbriteapi.com/v3/events/search/"
    
    params = {
    "location.address": city_name,
    "expand": "venue",
    "q": "music",  # ← Event category/keyword required
    "page": 1,
}

    headers = {
        "Authorization": "Bearer LD2HCX4QS7OHAQJC44U7"  
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()

        for event in data["events"]:
            name = event["name"]["text"]
            date = event["start"]["local"]
            venue = event["venue"]["name"]
            event_info = f"Event: {name}\nDate: {date}\nVenue: {venue}\n\n"
            results_box.insert(tk.END, event_info)
    else:
        print("Failed to fetch data:", response.status_code)



def handle_search():
    user_input = city_entry.get()
    print("You entered:", user_input)
    get_eventbrite_events(user_input)


search_button = tk.Button(root, text="Search Events", command=handle_search)
search_button.pack()




root.mainloop()
