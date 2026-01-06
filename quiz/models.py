
# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from video.models import Video

User = get_user_model()

class Question(models.Model):
    text = models.CharField(max_length=255)
    video = models.ForeignKey("video.Video", on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return self.text


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class UserQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey("video.Video", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "video")