from rest_framework import serializers
from .models import Story, StoryPage



class StoryPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryPage
        fields = ["id", "page_number", "image", "description"]


class StorySerializer(serializers.ModelSerializer):
    pages = StoryPageSerializer(many=True, read_only=True)
    class Meta:
        model = Story
        fields = ["id", "title", "cover_image", "pages", "created_at"]

class StoryPageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryPage
        fields = ["page_number", "image", "description"]

class StoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["title", "cover_image"]
