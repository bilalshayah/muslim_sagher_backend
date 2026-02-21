from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from person.permissions import IsAdmin,IsChild
from .models import Video
from .serializer import VideoSerializer
from points.services import get_video_status


# Swagger
from drf_yasg import openapi
from utils.swagger import auto_swagger

 #إضافة فيديو بواسطة admin ضمن Dashboard

class VideoCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    @auto_swagger(
        description="إضافة فيديو جديد",
        request_body=VideoSerializer,
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
        request_body=VideoSerializer,
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
    description="حذف فيديو عبر ID",
     responses={
        200: openapi.Response("تم حذف الفيديو بنجاح")
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
        description="عرض جميع الفيديوهات مع حالتها (owned / able / disabled)",
    )
    def get(self, request):
        videos = Video.objects.all()

        data = []
        for video in videos:
            status = get_video_status(request.user, video)
            serialized = VideoSerializer(
                video,
                context={"request": request}
            ).data
            data.append({
                **serialized,
                "status": status,
                "cost_points": video.reward.cost_points if hasattr(video, "reward") else 0
            })

        return Response({
            "status": "success",
            "message": "تم جلب الفيديوهات",
            "data": data
        })
    
    

class VideoPlayView(APIView):
    permission_classes = [IsAuthenticated]

    @auto_swagger(description="تشغيل فيديو (فقط إذا كان مملوكًا)")
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)

        status_video = get_video_status(request.user, video)

        if status_video != "owned":
            return Response({
                "status": "error",
                "message": "لا يمكنك مشاهدة هذا الفيديو قبل شرائه",
                "data": {
                    "video_status": status_video
                }
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "status": "success",
            "message": "تم السماح بتشغيل الفيديو",
            "data": VideoSerializer(video,context={"request": request}).data
        }, status=status.HTTP_200_OK)    

