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

video_data_schema=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                    "title": openapi.Schema(type=openapi.TYPE_STRING, example="Video Title"),
                                    "description": openapi.Schema(type=openapi.TYPE_STRING, example="Video description"),
                                    "is_lock": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                                    "video": openapi.Schema(type=openapi.TYPE_STRING, example="http://example.com/video.mp4"),
                                }
                            )

#إضافة فيديو بواسطة admin ضمن Dashboard
class VideoCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="إضافة فيديو جديد",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('is_lock', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True),
        ],
        responses={
            201: openapi.Response(
                description="تمت إضافة الفيديو بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تمت إضافة الفيديو بنجاح"),
                        "data": video_data_schema

                    }
                )
            ),
            400: openapi.Response(
                description="بيانات غير صحيحة",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="بيانات غير صحيحة"),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
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

    @swagger_auto_schema(
        operation_description="تعديل فيديو موجود",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('is_lock', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
        ],
        responses={
            200: openapi.Response(
                description="تم تعديل الفيديو بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تم تعديل الفيديو بنجاح"),
                        "data": video_data_schema
                    }
                )
            ),
            400: openapi.Response(
                description="بيانات غير صحيحة",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="بيانات غير صحيحة"),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
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

    @swagger_auto_schema(
        operation_description="حذف فيديو",
        responses={
            200: openapi.Response(
                description="تم حذف الفيديو بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تم حذف الفيديو بنجاح"),
                        "data":openapi.Schema(type=openapi.TYPE_STRING, example=None)

                    }
                )
            )
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

    @swagger_auto_schema(
        operation_description="عرض الفيديوهات المتاحة للطفل (فقط غير المقفولة)",
        responses={
            200: openapi.Response(
                description="تم جلب الفيديوهات بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تم جلب الفيديوهات بنجاح"),
                        "data": video_data_schema

                    }
                )
            )
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
