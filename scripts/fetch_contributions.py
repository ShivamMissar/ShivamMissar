"""Scrape the public contributions calendar (no token needed) -> data/contributions.json

Uses the same HTML fragment your profile page loads:
https://github.com/users/<user>/contributions
"""
import json
import os
import re
import sys
from datetime import date

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "ShivamMissar")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "contributions.json")

resp = requests.get(f"https://github.com/users/{USER}/contributions",
                    headers={"User-Agent": "profile-readme-bot"}, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# tooltips carry the exact counts: "5 contributions on May 3rd." / "No contributions on ..."
tips = {}
for tip in soup.find_all("tool-tip"):
    m = re.match(r"\s*(No|\d[\d,]*) contribution", tip.get_text())
    if m and tip.get("for"):
        tips[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))

days = []
for td in soup.select("td.ContributionCalendar-day[data-date]"):
    level = int(td.get("data-level", 0))
    count = tips.get(td.get("id"))
    if count is None:  # older markup kept the count on the cell itself
        count = int(td.get("data-count", level))
    days.append({"date": td["data-date"], "count": count, "level": level})

if not days:
    sys.exit("no contribution cells found: GitHub's markup may have changed")

days.sort(key=lambda d: d["date"])
today = date.today().isoformat()
days = [d for d in days if d["date"] <= today]

# streaks: today with 0 doesn't break the current streak yet
longest = run = 0
for d in days:
    run = run + 1 if d["count"] else 0
    longest = max(longest, run)
current = 0
for i, d in enumerate(reversed(days)):
    if d["count"]:
        current += 1
    elif i == 0:
        continue
    else:
        break

best = max(days, key=lambda d: d["count"])
months = {}
for d in days:
    months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]

data = {
    "user": USER,
    "generated": today,
    "total": sum(d["count"] for d in days),
    "current_streak": current,
    "longest_streak": longest,
    "best_day": {"date": best["date"], "count": best["count"]},
    "months": months,
    "days": days,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(data, f, indent=1)
print(f"{data['total']} contributions over {len(days)} days -> {OUT}")
