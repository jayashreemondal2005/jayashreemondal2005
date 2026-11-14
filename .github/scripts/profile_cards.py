"""Renders the self-hosted glassy profile cards (activity, languages, quote, trophies, snake).

Runs automatically from .github/workflows/snake.yml and saves SVGs into assets/stats/
so every card and the contribution snake work reliably without external broken links.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import urllib.request

USER = os.environ.get("PROFILE_USER", "jayashreemondal2005")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def today_ist() -> dt.date:
    return dt.datetime.now(IST).date()


# Portfolio Glassy Lavender / Violet / Cyan palette
BG_START = "#F5F3FF"
BG_END = "#ECFEFF"
CARD_BG = "#FFFFFF"
BORDER = "#C4B5FD"
ACCENT = "#7C3AED"
ACCENT_2 = "#2563EB"
ACCENT_3 = "#06B6D4"
TEXT_MAIN = "#17162B"
TEXT_SOFT = "#3B3A56"
TEXT_MUTED = "#6A6B86"
SANS = "'Inter','Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
DISPLAY = "'Sora','Segoe UI',-apple-system,BlinkMacSystemFont,sans-serif"
SERIF = "'Playfair Display',Georgia,'Times New Roman',serif"

HEAT = ["#E9ECF8", "#DDD6FE", "#A78BFA", "#7C3AED", "#4C1D95"]
IGNORED_LANGUAGES = {"Dockerfile", "Shell", "Batchfile", "PowerShell", "Makefile"}
LANG_COLORS = ["#7C3AED", "#2563EB", "#06B6D4", "#EC4899", "#8B5CF6", "#3B82F6"]


def fetch(url: str, api: bool = False) -> bytes:
    headers = {"User-Agent": f"{USER}-profile-cards"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as res:
        return res.read()


def contribution_calendar() -> list[tuple[dt.date, int, int]]:
    """Returns (date, level, count) for the last year from the public calendar."""
    page = fetch(f"https://github.com/users/{USER}/contributions").decode("utf-8")
    cells = {}
    for tag in re.findall(r"<td[^>]*data-date=\"[^\"]+\"[^>]*>", page):
        date = re.search(r'data-date="([^"]+)"', tag).group(1)
        level = int(re.search(r'data-level="(\d)"', tag).group(1))
        cid = re.search(r'id="([^"]+)"', tag).group(1)
        cells[cid] = [dt.date.fromisoformat(date), level, 0]
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        m = re.match(r"\s*([\d,]+) contributions?", text)
        if cid in cells and m:
            cells[cid][2] = int(m.group(1).replace(",", ""))
    return sorted((tuple(v) for v in cells.values()), key=lambda c: c[0])


def streaks(days: list[tuple[dt.date, int, int]]) -> tuple[int, int]:
    longest = run = 0
    for _, _, count in days:
        run = run + 1 if count else 0
        longest = max(longest, run)
    current = 0
    rev = list(reversed(days))
    if rev and rev[0][2] == 0:
        rev = rev[1:]
    for _, _, count in rev:
        if not count:
            break
        current += 1
    return current, longest


def repositories() -> list[dict]:
    data = json.loads(fetch(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner", api=True))
    return [r for r in data if not r["fork"] and r["name"].lower() != USER.lower()]


def languages(repos: list[dict]) -> list[tuple[str, float]]:
    totals: dict[str, float] = {}
    for repo in repos:
        try:
            langs = json.loads(fetch(repo["languages_url"], api=True))
        except Exception:
            continue
        for name, size in langs.items():
            if name not in IGNORED_LANGUAGES:
                totals[name] = totals.get(name, 0.0) + min(size, 120_000)
    total = sum(totals.values()) or 1.0
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    top = [(k, v / total * 100) for k, v in ranked[:5]]
    rest = 100 - sum(p for _, p in top)
    if rest > 0.5:
        if len(ranked) == 6:
            top.append((ranked[5][0], rest))
        else:
            top.append(("Other", rest))
    return top


def shell(w: int, h: int, body: str, title: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#F3EFFE"/>
      <stop offset="0.5" stop-color="#EEF2FF"/>
      <stop offset="1" stop-color="#ECFEFF"/>
    </linearGradient>
    <linearGradient id="jmGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7C3AED"/>
      <stop offset="0.5" stop-color="#2563EB"/>
      <stop offset="1" stop-color="#06B6D4"/>
    </linearGradient>
    <radialGradient id="orb1" cx="0.15" cy="0.15" r="0.6">
      <stop offset="0" stop-color="#A78BFA" stop-opacity="0.28"/>
      <stop offset="1" stop-color="#A78BFA" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="orb2" cx="0.88" cy="0.82" r="0.6">
      <stop offset="0" stop-color="#22D3EE" stop-opacity="0.24"/>
      <stop offset="1" stop-color="#22D3EE" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" rx="18" fill="url(#bgGrad)"/>
  <rect width="{w}" height="{h}" rx="18" fill="url(#orb1)"/>
  <rect width="{w}" height="{h}" rx="18" fill="url(#orb2)"/>
  <rect x="10" y="10" width="{w - 20}" height="{h - 20}" rx="14" fill="#FFFFFF" fill-opacity="0.76" stroke="#C4B5FD" stroke-opacity="0.65" stroke-width="1.2"/>
  <rect x="28" y="10" width="{w - 56}" height="3" rx="1.5" fill="url(#jmGrad)"/>
{body}
</svg>
"""


def label(x: float, y: float, text: str, size: int = 11, fill: str = ACCENT, anchor: str = "start", spacing: float = 1.8) -> str:
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{SANS}" font-size="{size}" font-weight="700" '
            f'letter-spacing="{spacing}" text-anchor="{anchor}">{html.escape(text)}</text>')


def activity_card(days, repo_count: int) -> str:
    w, h = 880, 300
    total = sum(c for _, _, c in days)
    active = sum(1 for _, _, c in days if c)
    current, longest = streaks(days)
    metrics = [
        (f"{total:,}", "CONTRIBUTIONS"),
        (str(active), "ACTIVE DAYS"),
        (str(current), "CURRENT STREAK"),
        (str(longest), "LONGEST STREAK"),
        (str(repo_count), "PUBLIC REPOS"),
    ]
    body = [
        label(38, 44, "GITHUB ACTIVITY  ·  LAST 12 MONTHS"),
        label(w - 38, 44, f"UPDATED  ·  {today_ist():%d %b %Y}".upper(), fill=TEXT_MUTED, anchor="end", spacing=1.4),
    ]
    col = (w - 76) / len(metrics)
    for i, (value, name) in enumerate(metrics):
        cx = 38 + col * i + col / 2
        bx = 38 + col * i + 6
        body.append(f'<rect x="{bx:.1f}" y="60" width="{col - 12:.1f}" height="74" rx="10" fill="#F8FAFC" fill-opacity="0.9" stroke="#E2E8F0"/>')
        body.append(f'<text x="{cx:.1f}" y="98" fill="url(#jmGrad)" font-family="{DISPLAY}" font-size="28" font-weight="700" text-anchor="middle">{value}</text>')
        body.append(label(cx, 120, name, size=9, fill=TEXT_MUTED, anchor="middle", spacing=1.5))

    cell, gap = 11, 3
    weeks: list[list] = []
    for d in days:
        if not weeks or d[0].weekday() == 6:
            weeks.append([])
        weeks[-1].append(d)
    grid_w = len(weeks) * (cell + gap) - gap
    x0 = (w - grid_w) / 2
    y0 = 174
    last_month = None
    for wi, week in enumerate(weeks):
        for d, level, count in week:
            row = (d.weekday() + 1) % 7
            x = x0 + wi * (cell + gap)
            y = y0 + row * (cell + gap)
            tip = f"{count} contribution{'s' if count != 1 else ''} on {d:%d %b %Y}"
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[level]}"><title>{tip}</title></rect>')
        first = week[0][0]
        if first.month != last_month and first.day <= 7:
            body.append(label(x0 + wi * (cell + gap), y0 - 9, first.strftime("%b").upper(), size=9, fill=TEXT_MUTED, spacing=1.0))
            last_month = first.month
    lx = x0 + grid_w - 5 * (cell + gap) - 42
    body.append(label(lx - 6, h - 22, "LESS", size=9, fill=TEXT_MUTED, anchor="end", spacing=1.0))
    for i, colr in enumerate(HEAT):
        body.append(f'<rect x="{lx + i * (cell + gap):.1f}" y="{h - 31}" width="{cell}" height="{cell}" rx="2.5" fill="{colr}"/>')
    body.append(label(lx + 5 * (cell + gap) + 4, h - 22, "MORE", size=9, fill=TEXT_MUTED, spacing=1.0))
    return shell(w, h, "\n".join("  " + b for b in body), "GitHub activity")


def languages_card(langs) -> str:
    w, h = 430, 250
    body = [label(32, 44, "LANGUAGES  ·  IN MY REPOSITORIES")]
    x, bar_w = 32, w - 64
    for i, (name, pct) in enumerate(langs):
        seg = bar_w * pct / 100
        body.append(f'<rect x="{x:.1f}" y="62" width="{max(seg - 2, 1):.1f}" height="10" rx="3" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
        x += seg
    for i, (name, pct) in enumerate(langs):
        cx = 32 + (i % 2) * 190
        cy = 110 + (i // 2) * 40
        body.append(f'<rect x="{cx}" y="{cy - 10}" width="11" height="11" rx="3" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
        body.append(f'<text x="{cx + 20}" y="{cy}" fill="{TEXT_MAIN}" font-family="{SANS}" font-size="14" font-weight="600">{html.escape(name)}</text>')
        body.append(f'<text x="{cx + 170}" y="{cy}" fill="{ACCENT}" font-family="{DISPLAY}" font-size="14" font-weight="700" text-anchor="end">{pct:.1f}%</text>')
    return shell(w, h, "\n".join("  " + b for b in body), "Most used languages")


QUOTES = [
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Simple things should be simple, complex things should be possible.", "Alan Kay"),
    ("Design is not just what it looks like and feels like. Design is how it works.", "Steve Jobs"),
    ("Controlling complexity is the essence of computer programming.", "Brian Kernighan"),
    ("Software is a great combination between artistry and engineering.", "Bill Gates"),
]


def wrap(text: str, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def quote_card(today: dt.date) -> str:
    w, h = 430, 250
    text, author = QUOTES[today.toordinal() % len(QUOTES)]
    lines = wrap(text, 36)
    size = 18 if len(lines) <= 3 else 16
    lh = size + 9
    top = 102 if len(lines) <= 3 else 94
    body = [
        label(32, 44, "DEVELOPER QUOTE OF THE DAY"),
        f'<text x="{w - 30}" y="94" fill="url(#jmGrad)" fill-opacity="0.22" font-family="{SERIF}" font-size="92" text-anchor="end">&#8221;</text>',
    ]
    for i, line in enumerate(lines[:5]):
        body.append(f'<text x="32" y="{top + i * lh}" fill="{TEXT_MAIN}" font-family="{SERIF}" font-style="italic" font-size="{size}">{html.escape(line)}</text>')
    ay = top + min(len(lines), 5) * lh + 14
    body.append(f'<line x1="32" y1="{ay - 4}" x2="58" y2="{ay - 4}" stroke="url(#jmGrad)" stroke-width="2"/>')
    body.append(label(66, ay, author.upper(), size=10, fill=ACCENT_2, spacing=1.8))
    return shell(w, h, "\n".join("  " + b for b in body), "Quote of the day")


def trophies_card() -> str:
    w, h = 880, 175
    items = [
        ("EDUCATION", "B.Tech IT", "BCET · 2023–2027"),
        ("INTERNSHIP", "AI / ML Intern", "EDU TANTR · 2025"),
        ("TRAINING", "Java Full Stack", "Wipro TalentNext"),
        ("CERTIFIED", "8 Certificates", "OCI · Azure · IBM"),
        ("CLOUD & AI", "16+ Badges", "Google Study Jam"),
        ("HACKATHONS", "3x Code Jam", "BCET Code Vision"),
    ]
    body = [label(32, 42, "HIGHLIGHTS  ·  EDUCATION, INTERNSHIP & CREDENTIALS")]
    col = (w - 64) / len(items)
    for i, (tier, title, sub) in enumerate(items):
        x = 32 + col * i
        cx = x + col / 2
        body.append(f'<rect x="{x + 4:.1f}" y="56" width="{col - 8:.1f}" height="96" rx="10" fill="#F8FAFC" fill-opacity="0.92" stroke="#DDD6FE" stroke-width="1.2"/>')
        body.append(f'<circle cx="{cx:.1f}" cy="74" r="5" fill="url(#jmGrad)"/>')
        body.append(label(cx, 96, tier, size=9, fill=ACCENT, anchor="middle", spacing=1.4))
        body.append(f'<text x="{cx:.1f}" y="118" fill="{TEXT_MAIN}" font-family="{DISPLAY}" font-size="12.5" font-weight="700" text-anchor="middle">{html.escape(title)}</text>')
        body.append(f'<text x="{cx:.1f}" y="136" fill="{TEXT_MUTED}" font-family="{SANS}" font-size="10" text-anchor="middle">{html.escape(sub)}</text>')
    return shell(w, h, "\n".join("  " + b for b in body), "Highlights and credentials")


def snake_card(days) -> str:
    """Renders a self-hosted animated Contribution Snake SVG in the glassy portfolio palette."""
    w, h = 880, 195
    cell, gap = 11, 3
    weeks: list[list] = []
    for d in days:
        if not weeks or d[0].weekday() == 6:
            weeks.append([])
        weeks[-1].append(d)
    grid_w = len(weeks) * (cell + gap) - gap
    x0 = (w - grid_w) / 2
    y0 = 64

    body = [
        label(38, 42, "CONTRIBUTION SNAKE  ·  LIVE ANIMATED GRID"),
        label(w - 38, 42, f"@{USER}".upper(), fill=TEXT_MUTED, anchor="end", spacing=1.4),
    ]

    for wi, week in enumerate(weeks):
        for d, level, count in week:
            row = (d.weekday() + 1) % 7
            x = x0 + wi * (cell + gap)
            y = y0 + row * (cell + gap)
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[level]}"/>')

    # Build a smooth serpentine path across the grid so the violet-cyan snake glides across all rows
    pts = []
    max_w = len(weeks) - 1
    waypoints = [
        (0, 1), (12, 1), (12, 5), (26, 5), (26, 2), (39, 2), (39, 6), (max_w, 6),
        (max_w, 0), (32, 0), (32, 4), (16, 4), (16, 1), (0, 1)
    ]
    for wx, wy in waypoints:
        px = x0 + wx * (cell + gap) + cell / 2
        py = y0 + wy * (cell + gap) + cell / 2
        pts.append(f"{px:.1f},{py:.1f}")
    path_d = "M " + " L ".join(pts)

    body.append(f'<path id="snakeTrack" d="{path_d}" fill="none" stroke="none"/>')
    # 7 trailing segments for the snake body (head to tail)
    radii = [6.5, 5.8, 5.2, 4.6, 4.0, 3.4, 2.8]
    colors = ["#7C3AED", "#6D28D9", "#4F46E5", "#2563EB", "#0284C7", "#06B6D4", "#22D3EE"]
    for idx, (rad, colr) in enumerate(zip(radii, colors)):
        delay = idx * 0.16
        body.append(
            f'<circle r="{rad}" fill="{colr}" opacity="{1.0 - idx * 0.08:.2f}">'
            f'<animateMotion dur="14s" begin="-{delay:.2f}s" repeatCount="indefinite" rotate="auto">'
            f'<mpath href="#snakeTrack"/>'
            f'</animateMotion>'
            f'</circle>'
        )

    return shell(w, h, "\n".join("  " + b for b in body), "Animated Contribution Snake")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="assets/stats")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)

    days = contribution_calendar()
    repos = repositories()
    cards = {
        "activity.svg": activity_card(days, len(repos)),
        "languages.svg": languages_card(languages(repos)),
        "quote.svg": quote_card(today_ist()),
        "trophies.svg": trophies_card(),
        "snake.svg": snake_card(days),
    }
    for name, svg in cards.items():
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as fh:
            fh.write(svg)
        print("wrote", name)


if __name__ == "__main__":
    main()
