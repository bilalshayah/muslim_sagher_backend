from .models import Azkar
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

class AzkarSerializer(serializers.ModelSerializer):
    class Meta:
        model=Azkar
        fields=['id','title','description']
        read_only_fields=['id']