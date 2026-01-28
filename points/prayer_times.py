from praytimes import PrayTimes
from django.utils import timezone

DAMASCUS_LAT = 33.5138
DAMASCUS_LON = 36.2765
DAMASCUS_TZ = 3  # GMT+3

CALC_METHOD = "Egypt"  # طريقة حساب مناسبة لسوريا

def get_damascus_prayer_times():
    pt = PrayTimes(CALC_METHOD)
    today = timezone.localdate()

    times = pt.getTimes(
        (today.year, today.month, today.day),
        (DAMASCUS_LAT, DAMASCUS_LON),
        DAMASCUS_TZ
    )

    return {
        "fajr": times["fajr"],
        "sunrise": times["sunrise"],
        "dhuhr": times["dhuhr"],
        "asr": times["asr"],
        "maghrib": times["maghrib"],
        "isha": times["isha"],
    }