# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import DailyActivity, UserPoints,AzkarCategory,DailyAzkarStatus


def create_daily_azkar_records(activity):
    for category in AzkarCategory.objects.all():
        DailyAzkarStatus.objects.get_or_create(
            activity=activity,
            category=category,
            defaults={"done": False}
        )

def start_new_day_task():
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    # معالجة كل مستخدم على حدة
    for user in User.objects.all():
        try:
            prev_activity = DailyActivity.objects.get(user=user, date=yesterday)

            # خريطة النقاط (الفروض + الصيام)
            points_map = {
                "fajr": 2,
                "dhuhr": 2,
                "asr": 2,
                "maghrib": 2,
                "isha": 2,
                "fasting": 3,
            }

            # خصم النقاط عند التقصير
            for field, value in points_map.items():
                if getattr(prev_activity, field) is False:
                    prev_activity.daily_points -= value  # ← يسمح بالسالب

            prev_activity.save()

            # تحديث الرصيد الكلي
            user_points, _ = UserPoints.objects.get_or_create(user=user)
            user_points.total_points += prev_activity.daily_points
            user_points.save()

        except DailyActivity.DoesNotExist:
            # إذا لم يكن هناك سجل لليوم السابق، نتجاهل
            pass

        # إنشاء سجل جديد لليوم الحالي للمستخدم
        activity, _ =DailyActivity.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                "fajr": False, "dhuhr": False, "asr": False, "maghrib": False, "isha": False,
                "taraweeh": False, "fasting": False,
                "sunnah_fajr": False, "sunnah_dhuhr": False,
                "sunnah_maghrib": False, "sunnah_isha": False,
                "quran_pages": 0,
                "daily_points": 0,
            }
        )
        create_daily_azkar_records(activity)


def start():
    scheduler = BackgroundScheduler()
    # كل يوم الساعة 12 منتصف الليل
    scheduler.add_job(start_new_day_task, 'cron', hour=0, minute=0)
    scheduler.start()


