# investing_news_scraper.py
# Fetch economic calendar data from Investing.com with debug output

from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def fetch_investing_calendar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.investing.com/economic-calendar/", timeout=120000)
        page.wait_for_timeout(5000)

        # Debug: save screenshot and HTML snapshot
        page.screenshot(path="screenshot.png", full_page=True)
        with open("page_debug.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # Wait for table or rows
        try:
            page.wait_for_selector("table.genTbl.openTbl.ecEconomicTable", timeout=20000)
        except:
            print("❌ Failed to locate economic calendar table.")
            browser.close()
            return []

        rows = page.query_selector_all("table.genTbl.openTbl.ecEconomicTable > tbody > tr")
        print(f"📊 Found {len(rows)} economic calendar rows.")

        events = []
        for row in rows:
            time_el = row.query_selector(".time")
            currency_el = row.query_selector(".left.flagCur")
            event_el = row.query_selector(".event")
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
