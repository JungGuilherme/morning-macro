"""Fetches the 'Operações' Google Sheet (published as CSV) and writes it as
JSON. Requires env var SHEET_CSV_URL (GitHub Secret in Actions).
"""
import csv
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "operacoes.json"

CSV_URL = os.environ.get("SHEET_CSV_URL", "")

# Maps expected sheet header (case-insensitive, accents optional) -> JSON key
COLUMN_MAP = {
    "data": "data",
    "ativo": "ativo",
    "direção": "direcao",
    "direcao": "direcao",
    "entrada": "entrada",
    "preço entrada": "entrada",
    "preco entrada": "entrada",
    "stop": "stop",
    "alvo": "alvo",
    "status": "status",
    "comentário": "comentario",
    "comentario": "comentario",
}


def main():
    if not CSV_URL:
        print("SHEET_CSV_URL not set — writing empty operacoes.")
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text("[]", encoding="utf-8")
        return

    try:
        resp = requests.get(CSV_URL, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Sheet request failed: {e}")
        OUT_PATH.write_text("[]", encoding="utf-8")
        return

    reader = csv.DictReader(io.StringIO(resp.text))
    rows = []
    for raw_row in reader:
        row = {}
        for key, value in raw_row.items():
            if key is None:
                continue
            norm_key = COLUMN_MAP.get(key.strip().lower())
            if norm_key:
                row[norm_key] = (value or "").strip()
        if row.get("ativo"):
            rows.append(row)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} — {len(rows)} operações")


if __name__ == "__main__":
    main()
