
from django.db import models
from person.models import Person

class Video(models.Model):
    id = models.AutoField(primary_key=True)
    child = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Create your models here.
