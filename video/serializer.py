
from rest_framework import serializers
from .models import Video
from points.models import UserReward,UserPoints

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'video', 'is_lock', 'created_at']
        read_only_fields = ['id', 'created_at']
        
        def validate_video(self, value):
            max_size = 50 * 1024 * 1024  # 50MB
            if value.size > max_size:
                raise serializers.ValidationError("حجم الفيديو أكبر من 50MB")
            return value


