"""Fetches the economic calendar from Financial Modeling Prep and segments
events into brasil / eua / internacional buckets.

Requires env var FMP_API_KEY (GitHub Secret in Actions).
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "calendar.json"

API_KEY = os.environ.get("FMP_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/api/v3/economic_calendar"

COUNTRY_REGION = {
    "BR": "brasil",
    "US": "eua",
}
# Countries whose events count as "internacional" (broad macro relevance)
INTERNACIONAL_COUNTRIES = {"CN", "EU", "DE", "GB", "JP", "FR", "IT"}

IMPORTANCE_MAP = {0: "low", 1: "medium", 2: "high", 3: "high"}


def fetch_events():
    if not API_KEY:
        print("FMP_API_KEY not set — writing empty calendar.")
        return []
    today = datetime.now(timezone.utc).date()
    params = {
        "from": today.isoformat(),
        "to": (today + timedelta(days=1)).isoformat(),
        "apikey": API_KEY,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"FMP request failed: {e}")
        return []


def bucket_for(country: str):
    if country in COUNTRY_REGION:
        return COUNTRY_REGION[country]
    if country in INTERNACIONAL_COUNTRIES:
        return "internacional"
    return None


def main():
    raw_events = fetch_events()
    buckets = {"brasil": [], "eua": [], "internacional": []}

    for ev in raw_events:
        country = (ev.get("country") or "").upper()
        region = bucket_for(country)
        if region is None:
            continue

        impact_raw = ev.get("impact", "Low")
        importance = str(impact_raw).lower() if isinstance(impact_raw, str) else IMPORTANCE_MAP.get(impact_raw, "low")
        if importance == "low":
            continue  # keep calendar concise — medium/high only

        event_date = ev.get("date", "")
        time_str = "—"
        if event_date and "T" in event_date:
            time_str = event_date.split("T")[1][:5]
        elif event_date and " " in event_date:
            time_str = event_date.split(" ")[1][:5]

        title = ev.get("event", "Evento econômico")
        actual = ev.get("actual")
        forecast = ev.get("estimate")
        previous = ev.get("previous")
        extra = []
        if actual is not None:
            extra.append(f"Atual: {actual}")
        if forecast is not None:
            extra.append(f"Esperado: {forecast}")
        if previous is not None:
            extra.append(f"Anterior: {previous}")
        if extra:
            title = f"{title} ({', '.join(extra)})"

        buckets[region].append({
            "time": time_str,
            "title": title,
            "importance": importance,
        })

    for region in buckets:
        buckets[region].sort(key=lambda x: x["time"])

    data = {**buckets, "generated_at": datetime.now(timezone.utc).isoformat()}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} — brasil={len(buckets['brasil'])} eua={len(buckets['eua'])} internacional={len(buckets['internacional'])}")


if __name__ == "__main__":
    main()
