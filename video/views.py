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
from drf_yasg import openapi
from utils.swagger import auto_swagger

 #إضافة فيديو بواسطة admin ضمن Dashboard

class VideoCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    @auto_swagger(
        description="إضافة فيديو جديد",
        responses={
            201: openapi.Response("تمت إضافة الفيديو بنجاح",VideoSerializer)
        }
    )
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save()
            return Response({
                "status": "success",
                "message": "تمت إضافة الفيديو بنجاح",
                "data": VideoSerializer(video).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "بيانات غير صحيحة",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




#تعديل بيانات فيديو (تعديل  حقل واحد أو أكثر )
class VideoUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    @auto_swagger(
        description="تعديل فيديو موجود",
        responses={
            200: openapi.Response("تم تعديل الفيديو بنجاح", VideoSerializer)
        }
    )
    def put(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoSerializer(video, data=request.data, partial=True)

        if serializer.is_valid():
            video = serializer.save()
            return Response({
                "status": "success",
                "message": "تم تعديل الفيديو بنجاح",
                "data": VideoSerializer(video).data
            })

        return Response({
            "status": "error",
            "message": "بيانات غير صحيحة",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


#حذف فيديو ضمن dashboard
class VideoDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @auto_swagger(
        description="حذف فيديو",
        responses={
            200: openapi.Response("تم حذف الفيديو بنجاح", openapi.Schema(type=openapi.TYPE_STRING, example=None))
        }
    )
    def delete(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        video.delete()

        return Response({
            "status": "success",
            "message": "تم حذف الفيديو بنجاح",
            "data": None
        }, status=status.HTTP_200_OK)


#إظهار الفيديوهات غير المقفولة للطفل
class MyVideosView(APIView):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="عرض الفيديوهات المتاحة(فقط غير المقفولة)",
        responses={
            200: openapi.Response("تم جلب الفيديوهات بنجاح", VideoSerializer(many=True))
        }
    )
    def get(self, request):
        videos = Video.objects.filter(is_lock=False)
        serializer = VideoSerializer(videos, many=True)

        return Response({
            "status": "success",
            "message": "تم جلب الفيديوهات بنجاح",
            "data": serializer.data
        })
