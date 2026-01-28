# prayer_windows.py
from datetime import datetime, time
from django.utils import timezone
import pytz
from .prayer_times import get_damascus_prayer_times

VALID_PRAYERS = ["fajr", "dhuhr", "asr", "maghrib", "isha"]


def build_prayer_windows():
    times = get_damascus_prayer_times()

    def t(x):
        return datetime.strptime(x, "%H:%M").time()

    return {
        "fajr":    (t(times["fajr"]),    t(times["sunrise"])),
        "dhuhr":   (t(times["dhuhr"]),   t(times["asr"])),
        "asr":     (t(times["asr"]),     t(times["maghrib"])),
        "maghrib": (t(times["maghrib"]), t(times["isha"])),
        "isha":    (t(times["isha"]),    time(23, 59)),
    }


def is_within_prayer_time(prayer_name):
    windows = build_prayer_windows()
    damascus_tz = pytz.timezone("Asia/Damascus")
    now = datetime.now(damascus_tz).time()


    if prayer_name not in windows:
        return False

    start, end = windows[prayer_name]
    return start <= now <= end