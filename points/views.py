from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets
from .models import DailyActivity, UserPoints ,QuranProgress
from .serializers import DailyActivitySerializer, UserPointsSerializer
from utils.swagger import auto_swagger
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .services import mark_prayer, is_within_prayer_time,mark_fasting,mark_taraweeh,mark_sunnah,mark_azkar,mark_quran_reading,get_points_summary
from .prayer_utils import VALID_PRAYERS


class PrayerViewSet(viewsets.ViewSet):
    """
    API لتسجيل الصلوات اليومية للأطفال.
    """

    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="تسجيل صلاة مفروضة. يتحقق من اسم الصلاة ووقت الصلاة ثم يسجلها ويضيف النقاط.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "prayer": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="fajr",
                    description="اسم الصلاة (fajr, dhuhr, asr, maghrib, isha)"
                )
            },
            required=["prayer"]
        )
    )
    @action(detail=False, methods=["post"])
    def mark(self, request):
        prayer = request.data.get("prayer")

        # التحقق من اسم الصلاة
        if prayer not in VALID_PRAYERS:
            return Response({
                "status": "error",
                "message": "اسم الصلاة غير صالح",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من الوقت
        if not is_within_prayer_time(prayer):
            return Response({
                "status": "error",
                "message": "خرج وقت الصلاة",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # تسجيل الصلاة
        activity, points = mark_prayer(request.user, prayer)

        return Response({
            "status": "success",
            "message": "تم تسجيل الصلاة وإضافة النقاط",
            "data": {
                "added_points": points,
                "activity": DailyActivitySerializer(activity).data
            }
        }, status=status.HTTP_200_OK)



class FastingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="تسجيل صيام اليوم. إذا وضع الطفل ✔️ تُضاف النقاط مرة واحدة فقط.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "fasting": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    example=True,
                    description="ضع True عند وضع إشارة صح على الصيام"
                )
            },
            required=["fasting"]
        )
    )
    @action(detail=False, methods=['post'])
    def mark(self, request):
        if not request.data.get("fasting", False):
            return Response({
                "status": "error",
                "message": "يجب إرسال fasting = true",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        activity, points = mark_fasting(request.user)

        if points == 0:
            return Response({
                "status": "error",
                "message": "تم تسجيل الصيام مسبقًا",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "تم تسجيل الصيام وإضافة النقاط",
            "data": {
                "added_points": points,
                "activity": DailyActivitySerializer(activity).data
            }
        }, status=status.HTTP_200_OK)
    

class SunnahViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="تسجيل سنة (الفجر – الظهر – المغرب – العشاء).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "sunnah": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="fajr",
                    description="اسم السنة: fajr / dhuhr / maghrib / isha"
                )
            },
            required=["sunnah"]
        )
    )
    @action(detail=False, methods=['post'])
    def mark(self, request):
        sunnah = request.data.get("sunnah")

        if sunnah not in ["fajr", "dhuhr", "maghrib", "isha"]:
            return Response({
                "status": "error",
                "message": "اسم السنة غير صحيح"
            }, status=400)

        activity, points = mark_sunnah(request.user, sunnah)

        if points == 0:
            return Response({
                "status": "error",
                "message": "تم تسجيل هذه السنة مسبقًا"
            }, status=400)

        return Response({
            "status": "success",
            "message": "تم تسجيل السنة وإضافة النقاط",
            "data": {
                "added_points": points,
                "activity": DailyActivitySerializer(activity).data
            }
        })
    
class TaraweehViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="تسجيل صلاة التراويح. تُضاف النقاط مرة واحدة فقط."
    )
    @action(detail=False, methods=['post'])
    def mark(self, request):
        activity, points = mark_taraweeh(request.user)

        if points == 0:
            return Response({
                "status": "error",
                "message": "تم تسجيل التراويح مسبقًا"
            }, status=400)

        return Response({
            "status": "success",
            "message": "تم تسجيل التراويح وإضافة النقاط",
            "data": {
                "added_points": points,
                "activity": DailyActivitySerializer(activity).data
            }
        })
    

class AzkarMarkView(APIView):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="تسجيل أذكار فئة معينة وإضافة النقاط.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "category_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    example=1,
                    description="معرّف فئة الأذكار"
                )
            },
            required=["category_id"]
        )
    )
    def post(self, request):
        category_id = request.data.get("category_id")

        if not category_id:
            return Response({
                "status": "error",
                "message": "يجب إرسال category_id"
            }, status=400)

        activity, points = mark_azkar(request.user, category_id)

        if points == 0:
            return Response({
                "status": "error",
                "message": "تم تسجيل أذكار هذه الفئة مسبقًا"
            }, status=400)

        return Response({
            "status": "success",
            "message": "تم تسجيل أذكار الفئة وإضافة النقاط",
            "added_points": points,
            "activity": DailyActivitySerializer(activity).data
        })

class QuranReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pages = int(request.data.get("pages", 0))

        if pages <= 0:
            return Response({"error": "عدد الصفحات غير صالح"}, status=400)

        activity, progress, added, reward = mark_quran_reading(request.user, pages)

        percentage = (progress.current_khatma_pages / 604) * 100

        return Response({
            "status": "success",
            "message": "تم تسجيل قراءة القرآن",
            "data": {
                "added_pages": added,
                "today_pages": activity.quran_pages,
                "total_pages_read": progress.total_pages_read,
                "completed_khatmas": progress.completed_khatmas,
                "current_khatma_percentage": round(percentage, 2),
                "reward": reward
            }
        })
    

class QuranProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progress, _ = QuranProgress.objects.get_or_create(user=request.user)

        percentage = (progress.current_khatma_pages / 604) * 100

        return Response({
            "status": "success",
            "message": "نسبة التقدم في الختمة الحالية",
            "data": {
                "completed_khatmas": progress.completed_khatmas,
                "current_khatma_pages": progress.current_khatma_pages,
                "current_khatma_percentage": round(percentage, 2),
                "total_pages_read": progress.total_pages_read,
            }
        })
    

from .services import get_points_summary


class PointsSummaryView(APIView):
    """
    API لإرجاع مجموع النقاط + تفصيل النقاط حسب النشاط.
    لا تُرجع أي تفاصيل يومية.
    """

    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="إرجاع مجموع النقاط الكلية للطفل مع تفصيل النقاط حسب النشاط (صلاة، صيام، قرآن، سنن، تراويح، أذكار).",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="ملخص النقاط"),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "total_points": openapi.Schema(type=openapi.TYPE_INTEGER, example=120),
                            "breakdown": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "prayers": openapi.Schema(type=openapi.TYPE_INTEGER, example=40),
                                    "sunnah": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
                                    "fasting": openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
                                    "taraweeh": openapi.Schema(type=openapi.TYPE_INTEGER, example=20),
                                    "quran": openapi.Schema(type=openapi.TYPE_INTEGER, example=30),
                                    "azkar": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                                }
                            )
                        }
                    )
                }
            )
        }
    )
    def get(self, request):
        data = get_points_summary(request.user)

        return Response({
            "status": "success",
            "message": "ملخص النقاط",
            "data": data
        })