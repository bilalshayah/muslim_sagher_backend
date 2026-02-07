from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from azkar.models import AzkarCategory
from django.utils import timezone

class DailyActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)

    # الصلوات المفروضة
    fajr = models.BooleanField(default=False)
    dhuhr = models.BooleanField(default=False)
    asr = models.BooleanField(default=False)
    maghrib = models.BooleanField(default=False)
    isha = models.BooleanField(default=False)

    # التراويح
    taraweeh = models.BooleanField(default=False)

    # الصيام
    fasting = models.BooleanField(default=False)

    # السنن
    sunnah_fajr = models.BooleanField(default=False)
    sunnah_dhuhr = models.BooleanField(default=False)
    sunnah_maghrib = models.BooleanField(default=False)
    sunnah_isha = models.BooleanField(default=False)

    # القرآن
    quran_pages = models.IntegerField(default=0)

    

    daily_points = models.IntegerField(default=0)
    class Meta:
        unique_together = ('user', 'date')
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
class UserPoints(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    points_spent_on_videos = models.IntegerField(default=0)
    points_from_exams = models.IntegerField(default=0)
    khatma_reward_points = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"
    

class DailyAzkarStatus(models.Model):
    activity = models.ForeignKey(DailyActivity, on_delete=models.CASCADE, related_name="azkar_status")
    category = models.ForeignKey(AzkarCategory, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('activity', 'category')


class QuranProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    total_pages_read = models.IntegerField(default=0)
    completed_khatmas = models.IntegerField(default=0)

    current_khatma_pages = models.IntegerField(default=0)
    reward_given_for_current_khatma = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.completed_khatmas} ختمات"
    


class Reward(models.Model):
    REWARD_TYPES = [("video", "Video"),("badge", "Badge"),("sticker", "Sticker"),("content", "Extra Content"),]

    title = models.CharField(max_length=100,help_text="اسم المكافأة الظاهر للطفل")

    description = models.TextField(blank=True,help_text="وصف المكافأة")

    type = models.CharField(max_length=20,choices=REWARD_TYPES)

    cost_points = models.PositiveIntegerField(help_text="عدد النقاط المطلوبة لشراء المكافأة")

    # 🔗 ربط المكافأة بالفيديو (في حال كانت مكافأة فيديو)
    video = models.OneToOneField("video.Video",on_delete=models.CASCADE,null=True,blank=True,related_name="reward")

    is_active = models.BooleanField(default=True,help_text="هل المكافأة متاحة حالياً")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.cost_points} pts)"



class UserReward(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="rewards")

    reward = models.ForeignKey(Reward,on_delete=models.CASCADE,related_name="owners")

    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "reward")
        verbose_name = "User Reward"
        verbose_name_plural = "User Rewards"

    def __str__(self):
        return f"{self.user} → {self.reward.title}"

class OfflinePointEvent(models.Model):
    EVENT_TYPES = [
        ("prayer", "Prayer"),
        ("fasting", "Fasting"),
        ("quran", "Quran"),
        ("azkar", "Azkar"),
        ("sunnah", "Sunnah"),
        ("taraweeh", "Taraweeh"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="offline_events")

    event_type = models.CharField(max_length=20,choices=EVENT_TYPES)

    points = models.PositiveIntegerField()

    synced_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.event_type} | +{self.points}"