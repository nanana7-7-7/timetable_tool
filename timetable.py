"""Googleカレンダー（ICS）から今週の時間割を出力するツール。

primary カレンダーなど、複数のカレンダーをまとめて読み、
月曜〜日曜の時間割をコンソールに表示し、timetable.md にも書き出す。
ICSの「秘密のアドレス」は config.json に書く（Gitには上げないこと）。
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import requests
from icalendar import Calendar
from recurring_ical_events import of

JST = ZoneInfo("Asia/Tokyo")
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
OUTPUT_PATH = os.path.join(HERE, "timetable.md")
WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]


def load_calendar_urls():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)["calendars"]
    sys.exit(
        "config.json が見つかりません。"
        "config.example.json を config.json にコピーして、"
        "Googleカレンダーの「iCal形式の秘密のアドレス」を貼ってください。"
    )


def week_range(today=None, weeks_ahead=0):
    today = today or datetime.now(JST).date()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=weeks_ahead)
    return monday, monday + timedelta(days=6)


def to_jst(dt):
    """date/datetime を (JSTのdate, JSTのdatetime or None) にそろえる。"""
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=JST)
        dt = dt.astimezone(JST)
        return dt.date(), dt
    return dt, None  # 終日イベント


def fetch_events(url, start_day, end_day):
    res = requests.get(url, timeout=30)
    res.raise_for_status()
    cal = Calendar.from_ical(res.content)
    events = []
    for comp in of(cal).between(start_day, end_day + timedelta(days=1)):
        s_day, s_dt = to_jst(comp.decoded("DTSTART"))
        _, e_dt = to_jst(comp.decoded("DTEND")) if comp.get("DTEND") else (s_day, None)
        events.append(
            {
                "day": s_day,
                "start": s_dt,
                "end": e_dt,
                "summary": str(comp.get("SUMMARY", "(無題)")),
            }
        )
    return events


def fmt_time_range(ev):
    if ev["start"] is None:
        return "終日"
    start = ev["start"].strftime("%H:%M")
    end = ev["end"].strftime("%H:%M") if ev["end"] else ""
    return f"{start}–{end}" if end else start


def group_by_day(events):
    by_day = {}
    for ev in events:
        by_day.setdefault(ev["day"], []).append(ev)
    for day_events in by_day.values():
        day_events.sort(
            key=lambda e: (
                e["start"] is not None,
                e["start"] or datetime.min.replace(tzinfo=JST),
            )
        )
    return by_day


def build_markdown(events, monday, sunday, label="今週"):
    by_day = group_by_day(events)
    lines = [f"# {label}の時間割（{monday:%m/%d}〜{sunday:%m/%d}）", ""]
    for i in range(7):
        day = monday + timedelta(days=i)
        lines.append(f"## {day:%m/%d}（{WEEKDAYS[i]}）")
        day_events = by_day.get(day, [])
        if not day_events:
            lines.append("- （予定なし）")
        for ev in day_events:
            lines.append(f"- {fmt_time_range(ev)} {ev['summary']}")
        lines.append("")
    return "\n".join(lines)


def build_plain(events, monday, sunday, label="今週"):
    by_day = group_by_day(events)
    lines = [f"{label}の時間割（{monday:%m/%d}〜{sunday:%m/%d}）", ""]
    for i in range(7):
        day = monday + timedelta(days=i)
        lines.append(f"■ {day:%m/%d}（{WEEKDAYS[i]}）")
        day_events = by_day.get(day, [])
        if not day_events:
            lines.append("  （予定なし）")
        for ev in day_events:
            lines.append(f"  {fmt_time_range(ev)} {ev['summary']}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Googleカレンダーから週の時間割を出力する")
    parser.add_argument("--next", action="store_true", help="来週の時間割を出力する")
    args = parser.parse_args()
    monday, sunday = week_range(weeks_ahead=1 if args.next else 0)
    label = "来週" if args.next else "今週"
    events = []
    seen = set()
    for url in load_calendar_urls():
        for ev in fetch_events(url, monday, sunday):
            key = (ev["day"], ev["start"], ev["summary"])
            if key not in seen:
                seen.add(key)
                events.append(ev)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(build_markdown(events, monday, sunday, label))
    print(build_plain(events, monday, sunday, label))
    print(f"（Markdown版は timetable.md に保存しました）")


if __name__ == "__main__":
    main()
