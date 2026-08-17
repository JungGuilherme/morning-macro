"""Pulls RSS feeds from Brazilian/international finance outlets, filters by
macro keywords, and writes data/news.json segmented by region.

No API key required — public RSS feeds only.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import feedparser

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "news.json"

# Each feed is tagged with its region bucket and a display source name.
FEEDS = [
    {"url": "https://www.infomoney.com.br/feed/", "source": "InfoMoney", "region": "brasil"},
    {"url": "https://www.moneytimes.com.br/feed/", "source": "Money Times", "region": "brasil"},
    {"url": "https://www.cnnbrasil.com.br/economia/feed/", "source": "CNN Brasil", "region": "brasil"},
    {"url": "https://www.investing.com/rss/news.rss", "source": "Investing.com", "region": "internacional"},
    {"url": "https://www.investing.com/rss/news_25.rss", "source": "Investing.com", "region": "eua"},
]

KEYWORDS = [
    "ibovespa", "selic", "copom", "ipca", "fed", "juros", "dólar", "dolar",
    "inflação", "inflacao", "pib", "bc", "banco central", "petróleo", "petroleo",
    "câmbio", "cambio", "b3", "bolsa", "treasury", "fomc", "payroll", "cpi",
    "opep", "commodities", "risco fiscal", "déficit", "deficit", "recuperação judicial",
    "eleição", "eleicao", "tarifa", "china", "japão", "japao",
]

MAX_PER_REGION = 8


def matches_keywords(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in KEYWORDS)


def clean_html(raw: str) -> str:
    return re.sub("<[^<]+?>", "", raw or "").strip()


def fetch_region(region: str) -> list:
    items = []
    for feed_cfg in FEEDS:
        if feed_cfg["region"] != region:
            continue
        parsed = feedparser.parse(feed_cfg["url"])
        for entry in parsed.entries:
            title = clean_html(entry.get("title", ""))
            summary = clean_html(entry.get("summary", ""))
            if not matches_keywords(title + " " + summary):
                continue
            published = entry.get("published", "") or entry.get("updated", "")
            items.append({
                "title": title,
                "link": entry.get("link", ""),
                "source": feed_cfg["source"],
                "published": published,
            })
    # de-dupe by title, keep first N
    seen = set()
    deduped = []
    for it in items:
        if it["title"] in seen:
            continue
        seen.add(it["title"])
        deduped.append(it)
    return deduped[:MAX_PER_REGION]


def main():
    data = {
        "brasil": fetch_region("brasil"),
        "eua": fetch_region("eua"),
        "internacional": fetch_region("internacional"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} — brasil={len(data['brasil'])} eua={len(data['eua'])} internacional={len(data['internacional'])}")


if __name__ == "__main__":
    main()
