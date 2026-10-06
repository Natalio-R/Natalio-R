"""Scrape the public contribution calendar (no token) -> data/contributions.json."""
import json
import os
import re
from collections import defaultdict
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "Natalio-R")
URL = f"https://github.com/users/{USER}/contributions"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    r = requests.get(URL, headers={"User-Agent": f"{USER}-profile-art"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # counts live in <tool-tip for="contribution-day-component-R-C">N contributions on ...</tool-tip>
    tips = {t["for"]: t.get_text(strip=True) for t in soup.find_all("tool-tip") if t.get("for")}
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        m = re.match(r"([\d,]+) contributions?", tips.get(td.get("id"), ""))
        days.append({
            "date": td["data-date"],
            "count": int(m.group(1).replace(",", "")) if m else 0,
            "level": int(td.get("data-level", 0)),
        })
    if not days:
        raise SystemExit("No se encontraron días: ¿ha cambiado el HTML de GitHub?")
    return sorted(days, key=lambda d: d["date"])


def streaks(days):
    longest, run, start, best_range = 0, 0, None, None
    for d in days:
        if d["count"]:
            run += 1
            start = start or d["date"]
            if run > longest:
                longest, best_range = run, (start, d["date"])
        else:
            run, start = 0, None
    # la racha actual no se rompe si hoy aún no hay contribuciones
    current, tail = 0, days[:-1] if days[-1]["count"] == 0 else days
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1
    return current, longest, best_range


def main():
    days = fetch_days()
    current, longest, longest_range = streaks(days)
    best = max(days, key=lambda d: d["count"])
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]
    data = {
        "user": USER,
        "generated": date.today().isoformat(),
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "longest_streak_range": longest_range,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": dict(monthly),
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print(f"{len(days)} días, {data['total']} contribuciones -> {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
