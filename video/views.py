from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Video
from .serializer import VideoSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class VideoCreateListView(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAdminUser]  # فقط الادمن

    @swagger_auto_schema(
        operation_summary="Create a new video for a child",
        operation_description="Admin can add a video for a specific child",
        responses={201: VideoSerializer, 400: "Bad Request"},
        tags=['Video Management']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List all videos",
        operation_description="Get list of all videos",
        responses={200: VideoSerializer(many=True)},
        tags=['Video Management']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# Create your views here.
