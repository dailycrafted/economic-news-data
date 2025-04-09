# investing_news_scraper.py
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

def fetch_investing_calendar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://www.investing.com/economic-calendar/", timeout=60000)
        
        # Wait for the calendar loader to disappear (ensures the table is populated)
        page.wait_for_selector("#economicCalendarData", timeout=30000)

        # Small wait for stability
        page.wait_for_timeout(5000)

        rows = page.query_selector_all("#economicCalendarData tr")
        events = []
        for row in rows:
            if "data-event-datetime" not in row.inner_html():
                continue
            time = row.query_selector(".time") or ""
            currency = row.query_selector(".left.flagCur") or ""
            event = row.query_selector(".event") or ""
            actual = row.query_selector(".act") or ""
            forecast = row.query_selector(".fore") or ""
            previous = row.query_selector(".prev") or ""
            impact = len(row.query_selector_all(".grayFullBullishIcon"))

            events.append({
                "time": time.inner_text().strip() if time else "",
                "currency": currency.inner_text().strip() if currency else "",
                "event": event.inner_text().strip() if event else "",
                "actual": actual.inner_text().strip() if actual else "",
                "forecast": forecast.inner_text().strip() if forecast else "",
                "previous": previous.inner_text().strip() if previous else "",
                "impact": impact
            })

        browser.close()
        return events

if __name__ == "__main__":
    events = fetch_investing_calendar()
    today = datetime.today().strftime("%Y-%m-%d")
    with open("news_schedule.json", "w", encoding="utf-8") as f:
        json.dump({"date": today, "events": events}, f, indent=2, ensure_ascii=False)
