from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets
from .models import DailyActivity, UserPoints ,QuranProgress,Reward,UserReward
from .serializers import DailyActivitySerializer, UserPointsSerializer,RewardSerializer,UserRewardSerializer
from utils.swagger import auto_swagger
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .services import mark_prayer, is_within_prayer_time,mark_fasting,mark_taraweeh,mark_sunnah,mark_azkar,mark_quran_reading,get_points_summary,get_rewards_status_for_user,unlock_reward_for_user,add_offline_event
from .prayer_utils import VALID_PRAYERS
from django.core.exceptions import ValidationError
from person.permissions import IsAdmin
from django.db import transaction

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
                "activity": DailyActivitySerializer(activity).data,
                
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
        fasting = request.data.get("fasting")
        
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
                "activity": DailyActivitySerializer(activity).data,
                
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
                "activity": DailyActivitySerializer(activity).data,
                
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
                "activity": DailyActivitySerializer(activity).data,
                
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
            "activity": DailyActivitySerializer(activity).data,
        })

class QuranReadView(APIView):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="تسجيل عدد الصفحات التي قرأها المستخدم من القرآن",
        request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["pages"],
    properties={
        "pages": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            example=5,
            description="عدد الصفحات التي قرأها المستخدم"
        )
    }
)
    )
    def post(self, request):
        pages = request.data.get("pages")

        try:
            pages = int(pages)
        except (TypeError, ValueError):
            return Response({
                "status": "error",
                "message": "عدد الصفحات يجب أن يكون رقمًا",
                "data": {}
            }, status=400)

        if pages <= 0:
            return Response({
                "status": "error",
                "message": "عدد الصفحات غير صالح",
                "data": {}
            }, status=400)

        activity, progress, added, reward = mark_quran_reading(request.user, pages)
        percentage = (progress.current_khatma_pages / 604) * 100

        return Response({
            "status": "success",
            "message": "تم تسجيل قراءة القرآن",
            "data": {
                "added_pages": added,
                "added_points":added,
                "today_pages": activity.quran_pages,
                "total_pages_read": progress.total_pages_read,
                "completed_khatmas": progress.completed_khatmas,
                "current_khatma_percentage": round(percentage, 2),
                "reward": reward,
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
    

#--------------------------------------------------------
#المكافآت CRUD 
#--------------------------------------------------------



class RewardViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
    # 🔹 Swagger generation
        if getattr(self, 'swagger_fake_view', False):
            return RewardSerializer

    # 🔹 unlock لا يحتاج serializer
        if self.action == "unlock":
            return None

        return RewardSerializer


    queryset = Reward.objects.all().order_by("-created_at")
    serializer_class = RewardSerializer
    def get_permissions(self):
        if self.action in ["list_for_user", "unlock"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    # -----------------------------
    # LIST
    # -----------------------------
    @auto_swagger(description=" عرض جميع المكافآت لل Admin")
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response({
                "status": "success",
                "message": "تم جلب المكافآت بنجاح",
                "data": serializer.data
            }, status=200)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "حدث خطأ أثناء جلب البيانات",
                "data": str(e)
            }, status=400)

    # -----------------------------
    # RETRIEVE
    # -----------------------------
    @auto_swagger(description="عرض مكافأة واحدة")
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return Response({
                "status": "success",
                "message": "تم جلب بيانات المكافأة",
                "data": serializer.data
            }, status=200)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "المكافأة غير موجودة",
                "data": str(e)
            }, status=404)

    # -----------------------------
    # CREATE
    # -----------------------------
    @auto_swagger(description="إنشاء مكافأة جديدة", request_body=RewardSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                "status": "success",
                "message": "تم إنشاء المكافأة بنجاح",
                "data": serializer.data
            }, status=201)

        except ValidationError as e:
            return Response({
                "status": "error",
                "message": "خطأ في البيانات",
                "data": e.message_dict
            }, status=400)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "حدث خطأ أثناء إنشاء المكافأة",
                "data": str(e)
            }, status=400)

    # -----------------------------
    # UPDATE
    # -----------------------------
    @auto_swagger(description="تعديل مكافأة", request_body=RewardSerializer)
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                "status": "success",
                "message": "تم تعديل المكافأة بنجاح",
                "data": serializer.data
            }, status=200)

        except ValidationError as e:
            return Response({
                "status": "error",
                "message": "خطأ في البيانات",
                "data": e.message_dict
            }, status=400)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "حدث خطأ أثناء تعديل المكافأة",
                "data": str(e)
            }, status=400)

    # -----------------------------
    # DELETE
    # -----------------------------
    @auto_swagger(description="حذف مكافأة")
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()

            return Response({
                "status": "success",
                "message": "تم حذف المكافأة بنجاح",
                "data": None
            }, status=200)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "حدث خطأ أثناء حذف المكافأة",
                "data": str(e)
            }, status=400)
    
    @auto_swagger(description=" عرض المكافآت مع حالتها بالنسبة للمستخدم للطفل")
    @action(detail=False, methods=["get"])
    def list_for_user(self, request):
        data = get_rewards_status_for_user(request.user)

        return Response({
            "status": "success",
            "message": "تم جلب المكافآت",
            "data": data
        }, status=200)
    

    @action(detail=True, methods=["post"])
    @auto_swagger(description="شراء مكافأة وخصم النقاط",request_body=None)
    def unlock(self, request, pk=None):
        result = unlock_reward_for_user(request.user, pk)

        rewards = get_rewards_status_for_user(request.user)

        if result["status"] == "owned":
            return Response({
                "status": "success",
                "message": "المكافأة مفتوحة مسبقًا",
                "data": {
                    "remaining_points": result["points"],
                    "rewards": rewards
                }
            })

        if result["status"] == "not_enough_points":
            return Response({
                "status": "error",
                "message": "النقاط غير كافية",
                "data": {
                    "remaining_points": result["points"],
                    "rewards": rewards
                }
            }, status=400)

        return Response({
            "status": "success",
            "message": "تم فتح المكافأة بنجاح",
            "data": {
                "remaining_points": result["points"],
                "rewards": rewards
            }
        })


class OfflineSyncView(APIView):
    permission_classes = [IsAuthenticated]

    @auto_swagger(
        description="مزامنة نقاط تم تحصيلها أثناء عدم الاتصال بالإنترنت",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["event", "points"],
            properties={
                "event": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="fasting"
                ),
                "points": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    example=6
                ),
            }
        )
    )
    def post(self, request):
        event_type = request.data.get("event")
        points = request.data.get("points")

        try:
            total = add_offline_event(
                user=request.user,
                event_type=event_type,
                points=int(points)
            )
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e),
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "تمت مزامنة النقاط بنجاح",
            "data": {
                "total_points": total
            }
        })