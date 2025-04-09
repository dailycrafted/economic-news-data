# investing_news_scraper.py
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

def fetch_investing_calendar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.investing.com/economic-calendar/", timeout=60000)

        # Accept cookies if popup appears
        try:
            page.click('button:has-text("I Accept")', timeout=5000)
        except:
            pass

        page.wait_for_selector(".economicCalendar", timeout=15000)

        events = []

        rows = page.query_selector_all("tr.js-event-item")
        for row in rows:
            time = row.query_selector(".time")?.inner_text().strip()
            currency = row.query_selector(".left flagCur")?.inner_text().strip()
            event_name = row.query_selector(".event")?.inner_text().strip()
            impact = len(row.query_selector_all(".grayFullBullishIcon"))  # 1–3
            actual = row.query_selector(".act")?.inner_text().strip()
            forecast = row.query_selector(".fore")?.inner_text().strip()
            previous = row.query_selector(".prev")?.inner_text().strip()

            if time and currency and event_name:
                events.append({
                    "datetime": time,
                    "currency": currency,
                    "event": event_name,
                    "impact": impact,
                    "actual": actual,
                    "forecast": forecast,
                    "previous": previous
                })

        browser.close()
        return events

if __name__ == "__main__":
    events = fetch_investing_calendar()
    today = datetime.today().strftime("%Y-%m-%d")
    with open("news_schedule.json", "w", encoding="utf-8") as f:
        json.dump({"date": today, "events": events}, f, indent=2, ensure_ascii=False)
