from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from person.permissions import IsAdmin,IsChild
from .models import Video
from .serializer import VideoSerializer


# Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


#إضافة فيديو بواسطة admin ضمن Dashboard
class VideoCreateView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    parser_classes = [MultiPartParser, FormParser]


    @swagger_auto_schema(
        operation_description="إضافة فيديو جديد ",
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                'description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'is_lock', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False
            ),
            openapi.Parameter(
                'video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True
            ),
        ],
        responses={201: VideoSerializer}
    )
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#تعديل بيانات فيديو (تعديل  حقل واحد أو أكثر )
class VideoUpdateView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="تعديل فيديو موجود",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('is_lock', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
        ],
        responses={200: VideoSerializer}
    )
    def put(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoSerializer(video, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#حذف فيديو ضمن dashboard
class VideoDeleteView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]

    @swagger_auto_schema(
        operation_description="حذف فيديو",
        responses={204: "Deleted Successfully"}
    )
    def delete(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        video.delete()
        return Response({"message": "Video deleted"}, status=status.HTTP_204_NO_CONTENT)


#إظهار الفيديوهات غير المقفولة للطفل
class MyVideosView(APIView):
    permission_classes = [IsAuthenticated,IsChild]

    @swagger_auto_schema(
        operation_description="عرض الفيديوهات المتاحة للطفل (فقط غير المقفولة)",
        responses={200: VideoSerializer(many=True)}
    )
    def get(self, request):


        # جلب الفيديوهات غير المقفولة فقط
        videos = Video.objects.filter(is_lock=False)

        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

