from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from azkar.models import AzkarCategory

class DailyActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

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
    

# class Reward(models.Model):
#     REWARD_TYPES = [
#         ("video", "Short Video"),
#         ("sticker", "Sticker"),
#         ("badge", "Badge"),
#         ("video_pack", "Video Pack"),
#     ]

#     type = models.CharField(max_length=20, choices=REWARD_TYPES)
#     required_points = models.IntegerField()
#     title = models.CharField(max_length=100)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return f"{self.title} ({self.required_points} pts)"


# class UserReward(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
#     unlocked_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("user", "reward")

#     def __str__(self):
#         return f"{self.user.username} unlocked {self.reward.title}"