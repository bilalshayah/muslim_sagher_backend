
from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'video', 'is_lock', 'created_at']
        read_only_fields = ['id', 'created_at']

    

