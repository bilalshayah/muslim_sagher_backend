from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('child', 'Child'),
    ('admin', 'Admin'),
)

class Person(AbstractUser):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default="child")
    email=models.EmailField(null=True,blank=True)
    father_name=models.CharField(max_length=100,null=True,blank=True)
    mother_name=models.CharField(max_length=100,null=True,blank=True)
    birth_date=models.DateField(null=True,blank=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    # username موجود من AbstractUser
    # password موجود من AbstractUser

    REQUIRED_FIELDS = ['name', 'mobile']  
    def __str__(self):
        return self.name
    
