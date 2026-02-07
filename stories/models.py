from django.db import models

# Create your models here.
class Story(models.Model):
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to="stories/covers/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class StoryPage(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="pages"
    )
    page_number = models.PositiveIntegerField()
    image = models.ImageField(upload_to="stories/pages/", null=True, blank=True)
    description = models.TextField()

    class Meta:
        ordering = ["page_number"]
        unique_together = ("story", "page_number")


    def __str__(self):
        return f"{self.story.title} - Page {self.page_number}"