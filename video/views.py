# from django.shortcuts import render
# from rest_framework import generics, permissions
# from .models import Video
# from .serializer import VideoSerializer,VideoUploadSerializer
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from rest_framework.parsers import MultiPartParser, FormParser


# class VideoCreateListView(generics.ListCreateAPIView):
#     queryset = Video.objects.all()
#     serializer_class = VideoSerializer
#     permission_classes = [permissions.IsAdminUser]  # فقط الادمن
#     parser_classes = [MultiPartParser, FormParser]

#     @swagger_auto_schema(
#         operation_summary="Create a new video for a child",
#         operation_description="Admin can add a video for a specific child",
#         request_body=VideoUploadSerializer
#         # responses={201: VideoSerializer, 400: "Bad Request"},
#         request_body=openapi.Schema(
#           type=openapi.TYPE_OBJECT,
#           required=['child', 'title', 'file'],
#           properties={
#              'child': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID للطفل'),
#              'title': openapi.Schema(type=openapi.TYPE_STRING, description='عنوان الفيديو'),
#              'file': openapi.Schema(type=openapi.TYPE_FILE, description='ملف الفيديو')
#     },
# ),
#          responses={201: VideoSerializer, 400: "Bad Request"},
#         tags=['Video Management']
#     )
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)

#     @swagger_auto_schema(
#         operation_summary="List all videos",
#         operation_description="Get list of all videos",
#         responses={200: VideoSerializer(many=True)},
#         tags=['Video Management']
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

# # Create your views here.

from rest_framework import generics, permissions,status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Video,Person
from .serializer import VideoSerializer, VideoUploadSerializer

class VideoCreateListView(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    
    permission_classes = [permissions.IsAuthenticated]  # فقط الادمن
    parser_classes = [MultiPartParser, FormParser]  # للسماح برفع الملفات

    @swagger_auto_schema(
        operation_summary="Create a new video for a child",
        operation_description="Admin can add a video for a specific child",
        request_body=VideoUploadSerializer,  # نستخدم السيريالايزر الخاص بالرفع
        responses={201: VideoSerializer, 400: "Bad Request"},
        tags=['Video Management']
    )
    def post(self, request, *args, **kwargs):
       
       child_id = request.data.get('child')
       if request.user.role != 'admin':
            return Response({"detail": "You are not admin"}, status=status.HTTP_403_FORBIDDEN)
       
       try:
            child = Person.objects.get(id=child_id)
       except Person.DoesNotExist:
            return Response({"detail": "Child not found"}, status=status.HTTP_404_NOT_FOUND)

       if child.role != 'child':
            return Response({"detail": "Selected user is not a child"}, status=status.HTTP_400_BAD_REQUEST)

        # حفظ الفيديو بعد التأكد من كل شيء
       serializer = VideoUploadSerializer(data=request.data)
       if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="List all videos",
        operation_description="Get list of all videos",
        responses={200: VideoSerializer(many=True)},
        tags=['Video Management']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    
