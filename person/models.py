from django.db import models
ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('child', 'Child'),
)

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    mobile = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='child')

    def __str__(self):
        return self.name

# Create your models here.
