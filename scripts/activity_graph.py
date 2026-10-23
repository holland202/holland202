#!/usr/bin/env python3
"""Render the profile README's contribution-activity graph as an SVG.

Standard library only. Replaces the third-party activity-graph service, which
began returning HTTP 402 (DEPLOYMENT_DISABLED) in October 2026.

Data: the user's public contribution calendar, from the GitHub GraphQL API
(token in GITHUB_TOKEN), or a JSON file of [{"date": "YYYY-MM-DD", "count": N}]
given with --from-json.

If the data is missing or malformed the script exits 1 and writes nothing, so a
broken source never replaces a good image. The image states the date of its
last data point, so a stale image is visible as stale.

Usage:
  GITHUB_TOKEN=... python3 activity_graph.py --user holland202 --out activity.svg
  python3 activity_graph.py --from-json days.json --out activity.svg
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import tempfile
import urllib.request
from xml.sax.saxutils import escape

QUERY = ("query($login:String!){user(login:$login){contributionsCollection{"
         "contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}")

# Colours of the graph this replaces (react-dark theme with the README's overrides).
BG, TITLE, LINE, AREA, POINT = "#0d1117", "#34d399", "#22d3ee", "#34d399", "#a78bfa"
GRID, MUTED, FAINT = "#21262d", "#8b949e", "#6e7681"
FONT = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
W, H = 900, 320
LEFT, RIGHT, TOP, BOTTOM = 56, 28, 70, 54


class DataError(Exception):
    pass


def fetch(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json",
                 "User-Agent": "profile-activity-graph"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("errors"):
        raise DataError("GraphQL errors: %s" % data["errors"])
    user = (data.get("data") or {}).get("user")
    if not user:
        raise DataError("user %r not found" % login)
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [{"date": d["date"], "count": d["contributionCount"]}
            for w in weeks for d in w["contributionDays"]]


def validate(days, n):
    """Return the last n days as [(date, count)], or raise DataError."""
    if not isinstance(days, list) or not days:
        raise DataError("no contribution data")
    out = []
    for d in days:
        try:
            date = dt.date.fromisoformat(d["date"])
            count = d["count"]
        except (KeyError, TypeError, ValueError) as e:
            raise DataError("malformed day %r: %s" % (d, e))
        if type(count) is not int or count < 0:
            raise DataError("bad count %r on %s" % (count, date))
        out.append((date, count))
    for (a, _), (b, _) in zip(out, out[1:]):
        if b - a != dt.timedelta(days=1):
            raise DataError("dates not contiguous: %s then %s" % (a, b))
    if len(out) < n:
        raise DataError("only %d days of data, need %d" % (len(out), n))
    return out[-n:]


NICE_TENTHS = (10, 12, 16, 20, 24, 30, 40, 50, 60, 80)


def nice_max(m):
    """Smallest 'nice' integer >= m (1, 1.2, 1.6, 2, 2.4, 3, 4, 5, 6, 8 x 10^k) that splits into 4 integer ticks."""
    if m <= 4:
        return 4
    k = 0
    while True:
        for c in NICE_TENTHS:
            tenths = c * 10 ** k
            if tenths % 10 == 0 and tenths // 10 >= m and (tenths // 10) % 4 == 0:
                return tenths // 10
        k += 1


def label(d):
    return d.strftime("%b ") + str(d.day)


def render(series):
    n = len(series)
    counts = [c for _, c in series]
    total, peak = sum(counts), max(counts)
    ymax = nice_max(peak)
    pw, ph = W - LEFT - RIGHT, H - TOP - BOTTOM

    def x(i):
        return LEFT + (pw * i / (n - 1) if n > 1 else pw / 2)

    def y(c):
        return TOP + ph - ph * c / ymax

    first, last = series[0][0], series[-1][0]
    peak_day = series[counts.index(peak)][0]
    desc = ("%d contributions from %s to %s; busiest day %s with %d."
            % (total, first.isoformat(), last.isoformat(), peak_day.isoformat(), peak))
    p = []
    p.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
             'role="img" aria-labelledby="t d">' % (W, H, W, H))
    p.append('<title id="t">Contribution activity, last %d days</title>' % n)
    p.append('<desc id="d">%s</desc>' % escape(desc))
    p.append('<rect width="%d" height="%d" rx="6" fill="%s"/>' % (W, H, BG))
    p.append('<g font-family="%s">' % FONT)
    p.append('<text x="%d" y="32" font-size="18" font-weight="600" fill="%s">Contribution activity</text>'
             % (LEFT, TITLE))
    p.append('<text x="%d" y="52" font-size="12" fill="%s">Last %d days · %s contributions</text>'
             % (LEFT, MUTED, n, format(total, ",")))
    for k in range(5):
        v = ymax * k // 4
        yy = y(v)
        p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                 % (LEFT, yy, W - RIGHT, yy, GRID))
        p.append('<text x="%d" y="%.1f" font-size="11" fill="%s" text-anchor="end">%d</text>'
                 % (LEFT - 8, yy + 4, MUTED, v))
    step = max(1, math.ceil(n / 7))
    for i in range(n):
        if (n - 1 - i) % step == 0:
            p.append('<text x="%.1f" y="%d" font-size="11" fill="%s" text-anchor="middle">%s</text>'
                     % (x(i), H - BOTTOM + 20, MUTED, escape(label(series[i][0]))))
    pts = " ".join("%.1f,%.1f" % (x(i), y(c)) for i, c in enumerate(counts))
    base = y(0)
    p.append('<polygon points="%.1f,%.1f %s %.1f,%.1f" fill="%s" fill-opacity="0.18"/>'
             % (x(0), base, pts, x(n - 1), base, AREA))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, LINE))
    for i, c in enumerate(counts):
        p.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"><title>%s: %d</title></circle>'
                 % (x(i), y(c), POINT, series[i][0].isoformat(), c))
    p.append('<text x="%d" y="%d" font-size="10" fill="%s" text-anchor="end">'
             'Data through %s · generated in this repository</text>'
             % (W - RIGHT, H - 12, FAINT, last.isoformat()))
    p.append('</g></svg>')
    return "\n".join(p) + "\n"


def write_atomic(path, text):
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--user")
    ap.add_argument("--from-json")
    ap.add_argument("--days", type=int, default=31)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.days < 2:
        ap.error("--days must be at least 2")
    try:
        if a.from_json:
            with open(a.from_json, encoding="utf-8") as f:
                days = json.load(f)
        else:
            token = os.environ.get("GITHUB_TOKEN")
            if not a.user or not token:
                raise DataError("need --user and GITHUB_TOKEN (or --from-json)")
            days = fetch(a.user, token)
        series = validate(days, a.days)
    except (DataError, OSError, ValueError) as e:
        print("activity_graph: %s; nothing written" % e, file=sys.stderr)
        return 1
    write_atomic(a.out, render(series))
    print("activity_graph: wrote %s (%d days, %d contributions, data through %s)"
          % (a.out, len(series), sum(c for _, c in series), series[-1][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
