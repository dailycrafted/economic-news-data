# investing_news_scraper.py
# Fetch economic calendar data from Investing.com with debug output

from playwright.sync_api import sync_playwright
import json
from datetime import datetime, date
from zoneinfo import ZoneInfo

def fetch_investing_calendar():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.investing.com/economic-calendar/", timeout=60000, wait_until="domcontentloaded")
        
        page.wait_for_selector("tr.js-event-item", timeout=60000)

        rows = page.query_selector_all("tr.js-event-item")
        print(f"📊 Found {len(rows)} economic calendar rows.")

        events = []
        # Example: convert each event time from UTC to broker time
        today = datetime.utcnow().date()
        broker_timezone = ZoneInfo("Europe/Berlin")  # Replace with your broker's time zone

        for row in rows:
            time_el = row.query_selector(".js-time")
            currency_el = row.query_selector(".flagCur")
            event_el = row.query_selector(".event a")
            actual_el = row.query_selector(".act")
            forecast_el = row.query_selector(".fore")
            previous_el = row.query_selector(".prev")
            impact_icons = row.query_selector_all(".grayFullBullishIcon")

            time = time_el.inner_text().strip() if time_el else ""
            currency = currency_el.inner_text().strip() if currency_el else ""
            event = event_el.inner_text().strip() if event_el else ""
            actual = actual_el.inner_text().strip() if actual_el else ""
            forecast = forecast_el.inner_text().strip() if forecast_el else ""
            previous = previous_el.inner_text().strip() if previous_el else ""
            impact = len(impact_icons)
            
            # Apply filters (optional): only high/medium impact USD/EUR/GBP/JPY/CAD/AUD/NZD/CHF events
            if not event or currency not in ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "NZD", "CHF"] or impact < 2:
                continue

            # Convert to broker time and add timestamp
            try:
                # Combine date + time string into full datetime
                event_dt_utc = datetime.strptime(f"{today} {time}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("UTC"))
                event_dt_broker = event_dt_utc.astimezone(broker_timezone)

                # Add both formatted and UNIX timestamp
                broker_time_str = event_dt_broker.strftime("%H:%M")
                event_timestamp = int(event_dt_broker.timestamp())

            except Exception as e:
                print("⚠️ Time conversion failed:", e)
                broker_time_str = ""
                event_timestamp = 0
                
                events.append({
                    "time": time,
                    "broker_time": broker_time_str,  # Converted
                    "timestamp": event_timestamp,    # For direct comparison in MT5
                    "currency": currency,
                    "event": event,
                    "actual": actual,
                    "forecast": forecast,
                    "previous": previous,
                    "impact": impact
                })

        browser.close()
        return events

if __name__ == "__main__":
    events = fetch_investing_calendar()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with open("news_schedule.json", "w", encoding="utf-8") as f:
        json.dump({"date": today, "events": events}, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(events)} events to news_schedule.json")
