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
            time_element = row.query_selector(".time")
            time = time_element.inner_text().strip() if time_element else ""

            currency_element = row.query_selector(".left.flagCur")
            currency = currency_element.inner_text().strip() if currency_element else ""

            event_element = row.query_selector(".event")
            event_name = event_element.inner_text().strip() if event_element else ""

            impact = len(row.query_selector_all(".grayFullBullishIcon"))  # 1–3

            actual_element = row.query_selector(".act")
            actual = actual_element.inner_text().strip() if actual_element else ""

            forecast_element = row.query_selector(".fore")
            forecast = forecast_element.inner_text().strip() if forecast_element else ""

            previous_element = row.query_selector(".prev")
            previous = previous_element.inner_text().strip() if previous_element else ""

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
