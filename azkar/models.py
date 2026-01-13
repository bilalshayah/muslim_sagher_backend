from django.db import models

# Create your models here.
class AzkarCategory (models.Model):
    title=models.CharField(max_length=255,unique=True)
   
    def __str__(self):
        return self.title
    
class Azkar (models.Model):
    description=models.TextField()
    title=models.ForeignKey(AzkarCategory,on_delete=models.CASCADE,related_name="azkar")

    def __str__(self):
        return f"{self.title.title} - {self.description[:30]}..."
