# investing_news_scraper.py
# Fetch daily economic events from Investing.com hidden endpoint and save as news_schedule.json

import requests
import re
import json
from datetime import datetime

def fetch_investing_calendar():
    url = "https://ec.forexprostools.com/"
    params = {
        "columns": "exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous,exc_country,exc_name,exc_time",
        "importance": "1,2,3",
        "countries": "5,6,7,14,17,22,26,32,37,72",  # US, EU, UK, etc
        "calType": "day",
        "timezone": "60",
        "lang": "1"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception("Failed to fetch data")

    raw_text = response.text
    json_str = re.search(r'\((\[.*\])\)', raw_text).group(1)
    data = json.loads(json_str)

    events = []
    for item in data:
        events.append({
            "Event": item[7],
            "Country": item[6],
            "Currency": item[1],
            "Impact": ["Low", "Medium", "High"][int(item[2]) - 1],
            "Actual": item[3],
            "Forecast": item[4],
            "Previous": item[5],
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Time": item[8],
            "Pair": "XAUUSD"
        })

    with open("news_schedule.json", "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    print(f"✅ Saved {len(events)} events to news_schedule.json")

if __name__ == "__main__":
    fetch_investing_calendar()
