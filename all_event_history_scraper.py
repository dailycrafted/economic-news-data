
from playwright.sync_api import sync_playwright
import json
import time

EVENTS = [
    {"name": "U.S. Non-Farm Payrolls (NFP)", "url": "https://www.investing.com/economic-calendar/nonfarm-payrolls-227", "currency": "USD"},
    {"name": "U.S. Consumer Price Index (CPI)", "url": "https://www.investing.com/economic-calendar/cpi-733", "currency": "USD"},
    {"name": "CB Consumer Confidence Index (CCI)", "url": "https://www.investing.com/economic-calendar/cb-consumer-confidence-234", "currency": "USD"},
    {"name": "ISM Manufacturing PMI", "url": "https://www.investing.com/economic-calendar/ism-manufacturing-pmi-173", "currency": "USD"},
    {"name": "ISM Services PMI", "url": "https://www.investing.com/economic-calendar/ism-non-manufacturing-pmi-176", "currency": "USD"},
    {"name": "Core PCE Price Index", "url": "https://www.investing.com/economic-calendar/core-pce-price-index-233", "currency": "USD"},
    {"name": "Retail Sales", "url": "https://www.investing.com/economic-calendar/core-retail-sales-257", "currency": "USD"},
    {"name": "Initial Jobless Claims", "url": "https://www.investing.com/economic-calendar/initial-jobless-claims-294", "currency": "USD"},
    {"name": "U.S. Federal Reserve (FOMC Rate Decision)", "url": "https://www.investing.com/economic-calendar/interest-rate-decision-168", "currency": "USD"},
    {"name": "European Central Bank (ECB Rate Decision)", "url": "https://www.investing.com/economic-calendar/ecb-interest-rate-decision-168", "currency": "EUR"},
    {"name": "Bank of England (BOE Rate Decision)", "url": "https://www.investing.com/economic-calendar/boe-interest-rate-decision-164", "currency": "GBP"},
    {"name": "BOJ", "url": "https://www.investing.com/economic-calendar/boj-interest-rate-decision-157", "currency": "JPY"},
    {"name": "Inflation Expectations Reports", "url": "https://www.investing.com/economic-calendar/michigan-inflation-expectations-439", "currency": "USD"},
    {"name": "Canadian Employment Report & Unemployment Rate", "url": "https://www.investing.com/economic-calendar/employment-change-300", "currency": "CAD"},
    {"name": "Bank of Canada (BOC Rate Decision)", "url": "https://www.investing.com/economic-calendar/boc-interest-rate-decision-160", "currency": "CAD"},
    {"name": "Australian Employment Report", "url": "https://www.investing.com/economic-calendar/employment-change-301", "currency": "AUD"},
    {"name": "Reserve Bank of Australia (RBA Rate Decision)", "url": "https://www.investing.com/economic-calendar/rba-interest-rate-decision-242", "currency": "AUD"},
    {"name": "Crude Oil Inventories (U.S. Oil Market Report)", "url": "https://www.investing.com/economic-calendar/crude-oil-inventories-266", "currency": "USD"}
]

def scrape_all_events():
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for event in EVENTS:
            print(f"Scraping: {event['name']}")
            try:
                page.goto(event["url"], timeout=60000)
                page.wait_for_selector("table.genTbl.openTbl.ecHistoryTab", timeout=10000)
                time.sleep(1)

                rows = page.query_selector_all("table.genTbl.openTbl.ecHistoryTab tbody tr")

                for row in rows:
                    cols = row.query_selector_all("td")
                    if len(cols) < 6:
                        continue

                    date = cols[0].inner_text().strip()
                    time_text = cols[1].inner_text().strip()
                    actual = cols[2].inner_text().strip()
                    forecast = cols[3].inner_text().strip()
                    previous = cols[4].inner_text().strip()

                    all_data.append({
                        "Event": event["name"],
                        "Currency": event["currency"],
                        "Impact": "High",
                        "Date": date,
                        "Time": time_text,
                        "Actual": actual,
                        "Forecast": forecast,
                        "Previous": previous
                    })

                time.sleep(1)
            except Exception as e:
                print(f"Error scraping {event['name']}: {e}")

        browser.close()

    with open("all_event_history.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
    print("✅ all_event_history.json created")

if __name__ == "__main__":
    scrape_all_events()
