# investing_news_scraper.py
# Fetch economic calendar data from Investing.com with debug output

from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def fetch_investing_calendar():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.investing.com/economic-calendar/", timeout=60000, wait_until="domcontentloaded")

        # Add this before waiting — it helps debugging
        page.screenshot(path="screenshot_before_wait.png", full_page=True)
        with open("page_before_wait.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        
        page.wait_for_selector("tr.js-event-item", timeout=60000)

        rows = page.query_selector_all("tr.js-event-item")
        print(f"📊 Found {len(rows)} economic calendar rows.")

        events = []

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

            if event:
                events.append({
                    "time": time,
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
