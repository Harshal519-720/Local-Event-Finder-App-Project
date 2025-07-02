import flet as ft
import requests
import geocoder
from datetime import datetime, timedelta
from collections import defaultdict

def get_user_city():
    try:
        g = geocoder.ip("me")
        return g.city or ""
    except:
        return ""

def fetch_all_events(city, category):
    API_KEY = "qGDnOricwKqTRb66e5xyDWPYOWsQGDCT"
    classification = "" if category == "All" else f"&classificationName={category}"
    base_url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={API_KEY}&city={city}&size=200{classification}"
    all_events = []
    page = 0
    now = datetime.now().date()

    while True:
        url = f"{base_url}&page={page}"
        try:
            response = requests.get(url)
            data = response.json()

            if "_embedded" not in data or "events" not in data["_embedded"]:
                break

            events = data["_embedded"]["events"]
            for e in events:
                raw_date = e["dates"]["start"].get("localDate", "Unknown")
                try:
                    event_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                    if event_date < now:
                        continue
                except:
                    continue

                name = e.get("name", "N/A")
                raw_time = e["dates"]["start"].get("localTime", "Unknown")
                venue = e["_embedded"]["venues"][0].get("name", "Unknown Venue")
                url = e.get("url", "")
                images = e.get("images", [])
                image_url = images[0]["url"] if images else ""

                try:
                    date = event_date.strftime("%B %d, %Y")
                except:
                    date = raw_date

                try:
                    time_obj = datetime.strptime(raw_time, "%H:%M:%S") if len(raw_time) > 5 else datetime.strptime(raw_time, "%H:%M")
                    time = time_obj.strftime("%I:%M %p")
                except:
                    time = raw_time

                entry = {
                    "summary": f"🎉 {name}",
                    "venue": venue,
                    "date": date,
                    "time": time,
                    "url": url,
                    "image_url": image_url,
                    "event_date": event_date,
                    "raw_time": raw_time
                }

                all_events.append(entry)

            if page >= data.get("page", {}).get("totalPages", 0) - 1:
                break

            page += 1

        except Exception as e:
            all_events.append({"summary": f"❌ Error: {e}", "event_date": datetime.max})
            break

    if not all_events:
        return [{"summary": f"⚠️ No events found for '{city}'.", "event_date": datetime.max}]
    return sorted(all_events, key=lambda x: (x["event_date"], x["summary"]))

def main(page: ft.Page):
    page.title = "Eventure - Flet Edition"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme()
    page.window_width = 720
    page.window_height = 700

    language_options = ["English", "Español", "Français"]
    categories = ["All", "Music", "Sports", "Arts & Theater", "Film", "Miscellaneous"]

    translations = {
        "Enter City": {"English": "Enter City", "Español": "Ingrese ciudad", "Français": "Entrez une ville"},
        "Search": {"English": "🔍 Search", "Español": "🔍 Buscar", "Français": "🔍 Rechercher"},
        "Dark Mode": {"English": "Dark Mode", "Español": "Modo Oscuro", "Français": "Mode Sombre"},
        "Eventure": {"English": "Eventure", "Español": "Eventure", "Français": "Eventure"},
        "Venue": {"English": "Venue", "Español": "Lugar", "Français": "Lieu"},
        "Date": {"English": "Date", "Español": "Fecha", "Français": "Date"},
        "Time": {"English": "Time", "Español": "Hora", "Français": "Heure"}
    }

    language_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(lang) for lang in language_options], width=150, value="English"
    )

    def tr(key):
        lang = language_dropdown.value
        return translations.get(key, {}).get(lang, key)

    city_input = ft.TextField(label=tr("Enter City"), width=200, on_submit=lambda _: on_search_click(None))
    search_button = ft.ElevatedButton(tr("Search"), on_click=lambda e: on_search_click(e))
    dark_mode_switch = ft.Switch(label=tr("Dark Mode"), on_change=lambda e: toggle_theme())
    output_box = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    loading_indicator = ft.ProgressRing(visible=False)
    error_text = ft.Text("", color=ft.Colors.RED, visible=False)
    pagination_row = ft.Row([], alignment=ft.MainAxisAlignment.CENTER)

    category_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(cat) for cat in categories], width=200, value="All"
    )

    language_dropdown.on_change = lambda e: refresh_language()

    view_mode = "List"

    def set_view_mode(mode):
        nonlocal view_mode
        loading_indicator.visible = True
        page.update()
        view_mode = mode
        refresh_output()
        loading_indicator.visible = False
        page.update()

    def styled_toggle_button(label):
        return ft.TextButton(
            label,
            on_click=lambda e, l=label: set_view_mode(l),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_GREY_700 if view_mode == label else None,
                color=ft.Colors.WHITE if view_mode == label else ft.Colors.BLUE_GREY_900
            )
        )

    view_toggle_row = ft.Row([
        styled_toggle_button("List"),
        styled_toggle_button("Calendar")
    ], alignment=ft.MainAxisAlignment.CENTER)

    last_results = []
    current_page = 1
    events_per_page = 20

    def refresh_language():
        city_input.label = tr("Enter City")
        search_button.text = tr("Search")
        dark_mode_switch.label = tr("Dark Mode")
        page.controls[0].controls[0].text = tr("Eventure")
        refresh_output()
        page.update()

    def format_countdown(delta: timedelta):
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    def refresh_output():
        output_box.controls.clear()
        view_toggle_row.controls.clear()
        view_toggle_row.controls.extend([
            styled_toggle_button("List"),
            styled_toggle_button("Calendar")
        ])

        if view_mode == "Calendar":
            grouped = defaultdict(list)
            for event in sorted(last_results, key=lambda x: (x["event_date"], x["summary"])):
                grouped[event["date"]].append(event)
            for date, events in grouped.items():
                output_box.controls.append(ft.Text(date, size=20, weight="bold"))
                for event in events:
                    output_box.controls.append(render_event_card(event))
        else:
            start = (current_page - 1) * events_per_page
            end = start + events_per_page
            page_events = last_results[start:end]

            if len(page_events) == 1 and (
                page_events[0].get("summary", "").startswith("⚠️ No events found") or
                page_events[0].get("summary", "").startswith("❌ Error")
            ):
                output_box.controls.append(
                    ft.Text(page_events[0].get("summary", ""), size=18, weight="bold", color=ft.Colors.RED)
                )
                page.update()
                return

            for event in page_events:
                output_box.controls.append(render_event_card(event))

            render_pagination()
        page.update()

    def render_event_card(event):
        summary_text = ft.Text(event.get("summary", ""), size=16, weight="bold", expand=True,
                               color=ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK87)
        details = (
            f"🎪 {tr('Venue')}: {event.get('venue', 'Unknown')}\n"
            f"📅 {tr('Date')}: {event.get('date', 'Unknown')}\n"
            f"⏰ {tr('Time')}: {event.get('time', 'Unknown')}"
        )
        detail_text = ft.Text(details, expand=True, selectable=True,
                              color=ft.Colors.WHITE70 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK54)

        ticket_link = ft.Text(
            spans=[
                ft.TextSpan(
                    "🎟️ Tickets available here",
                    url=event.get("url", ""),
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.UNDERLINE,
                        color=ft.Colors.BLUE
                    )
                )
            ],
            selectable=True
        )

        countdown_text = ft.Text("", size=14, color=ft.Colors.RED_400)

        event_datetime = datetime.combine(event['event_date'], datetime.min.time())
        raw_time = event.get('raw_time', '')
        try:
            time_obj = datetime.strptime(raw_time, "%H:%M:%S") if len(raw_time) > 5 else datetime.strptime(raw_time, "%H:%M")
            event_datetime = event_datetime.replace(hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second)
        except:
            pass

        delta = event_datetime - datetime.now()
        if timedelta(0) < delta <= timedelta(days=2):
            countdown_text.value = f"⏳ Starts in: {format_countdown(delta)}"

        image = ft.Image(src=event.get("image_url", ""), width=180, height=100, border_radius=8) if event.get("image_url") else None

        text_column = ft.Column([summary_text, detail_text, ticket_link, countdown_text], expand=True)

        return ft.Container(
            content=ft.Row([image if image else ft.Container(), text_column], spacing=20),
            padding=12,
            border_radius=12,
            bgcolor=ft.Colors.BLUE_GREY_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.BLUE_GREY_800,
            shadow=ft.BoxShadow(blur_radius=8, color="#00000022")
        )

    def render_pagination():
        pagination_row.controls.clear()
        total_pages = (len(last_results) + events_per_page - 1) // events_per_page
        for i in range(1, total_pages + 1):
            style = ft.ButtonStyle(bgcolor="#444444" if page.theme_mode == ft.ThemeMode.DARK else '#e0e0e0') if i == current_page else None
            pagination_row.controls.append(ft.TextButton(str(i), on_click=lambda e, p=i: change_page(p), style=style))

    def change_page(page_num):
        nonlocal current_page
        current_page = page_num
        refresh_output()

    def toggle_theme():
        page.theme_mode = ft.ThemeMode.DARK if dark_mode_switch.value else ft.ThemeMode.LIGHT
        refresh_output()
        page.update()

    def on_search_click(e):
        nonlocal last_results, current_page
        error_text.visible = False
        city = city_input.value.strip()
        category = category_dropdown.value
        loading_indicator.visible = True
        output_box.controls.clear()
        pagination_row.controls.clear()
        page.update()
        try:
            last_results = fetch_all_events(city, category)
            current_page = 1
            refresh_output()
        except Exception as ex:
            error_text.value = str(ex)
            error_text.visible = True
        loading_indicator.visible = False
        page.update()

    city_row = ft.Row([
        city_input,
        category_dropdown,
        search_button,
        language_dropdown,
        dark_mode_switch
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    page.add(ft.Column([
        ft.Text(tr("Eventure"), size=32, weight="bold", color=ft.Colors.BLUE),
        city_row,
        view_toggle_row,
        loading_indicator,
        error_text,
        output_box,
        pagination_row
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))

    user_city = get_user_city()
    if user_city:
        city_input.value = user_city
        last_results.extend(fetch_all_events(user_city, category_dropdown.value))
        refresh_output()

ft.app(target=main, view=ft.WEB_BROWSER)
