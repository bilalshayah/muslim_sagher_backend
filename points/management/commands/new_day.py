from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from points.models import DailyActivity, UserPoints, AzkarCategory, DailyAzkarStatus

class Command(BaseCommand):
    help = "Daily task: create new activity and apply deductions"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        for user in User.objects.all():
            # معالجة اليوم السابق
            try:
                prev_activity = DailyActivity.objects.get(user=user, date=yesterday)

                points_map = {
                    "fajr": 2,
                    "dhuhr": 2,
                    "asr": 2,
                    "maghrib": 2,
                    "isha": 2,
                    "fasting": 3,
                }

                # خصم النقاط
                for field, value in points_map.items():
                    if getattr(prev_activity, field) is False:
                        prev_activity.daily_points -= value

                prev_activity.save()

                # تحديث الرصيد الكلي
                user_points, _ = UserPoints.objects.get_or_create(user=user)
                user_points.total_points += prev_activity.daily_points
                user_points.save()

            except DailyActivity.DoesNotExist:
                pass

            # إنشاء سجل جديد لليوم الحالي
            activity, _ = DailyActivity.objects.get_or_create(
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

            # إنشاء حالات الأذكار
            for category in AzkarCategory.objects.all():
                DailyAzkarStatus.objects.get_or_create(
                    activity=activity,
                    category=category,
                    defaults={"done": False}
                )

        self.stdout.write(self.style.SUCCESS("Daily task completed"))