from rest_framework import serializers
from .models import Video, Person

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'child', 'title', 'file', 'created_at']

    def validate_child(self, value):
        # نتأكد أن المستخدم المختار هو طفل فقط
        if value.role != 'child':
            raise serializers.ValidationError("يمكنك فقط اختيار طفل لإضافة الفيديو له.")
        return value
