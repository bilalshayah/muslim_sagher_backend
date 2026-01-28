from django.urls import path, include
from rest_framework.routers import DefaultRouter

# استيراد الـ ViewSets والـ APIViews
from .views import (
    PrayerViewSet,
    FastingViewSet,
    SunnahViewSet,
    TaraweehViewSet,
    AzkarMarkView,
    QuranReadView,
    QuranProgressView,
    PointsSummaryView
)

# 🔹 نستخدم Router لأن لدينا ViewSets (مثل الصلاة والصيام والسنن والتراويح)
router = DefaultRouter()

# ---------------------------------------------------------
# 1) تسجيل الصلوات الخمس
#    endpoint: POST /prayer/mark/
#    الهدف: تسجيل صلاة معينة وإضافة النقاط
# ---------------------------------------------------------
router.register(r'prayer', PrayerViewSet, basename='prayer')

# ---------------------------------------------------------
# 2) تسجيل صيام اليوم
#    endpoint: POST /fasting/mark/
#    الهدف: تسجيل صيام يوم واحد وإضافة النقاط
# ---------------------------------------------------------
router.register(r'fasting', FastingViewSet, basename='fasting')

# ---------------------------------------------------------
# 3) تسجيل السنن (الفجر – الظهر – المغرب – العشاء)
#    endpoint: POST /sunnah/mark/
#    الهدف: تسجيل سنة معينة وإضافة النقاط
# ---------------------------------------------------------
router.register(r'sunnah', SunnahViewSet, basename='sunnah')

# ---------------------------------------------------------
# 4) تسجيل صلاة التراويح
#    endpoint: POST /taraweeh/mark/
#    الهدف: تسجيل التراويح مرة واحدة يوميًا
# ---------------------------------------------------------
router.register(r'taraweeh', TaraweehViewSet, basename='taraweeh')

urlpatterns = [
    # 🔹 إدراج كل الـ ViewSets المسجلة في الـ Router
    path('', include(router.urls)),

    # ---------------------------------------------------------
    # 5) تسجيل الأذكار لفئة معينة
    #    endpoint: POST /azkar/mark/
    #    الهدف: تسجيل أذكار الصباح/المساء/النوم وإضافة النقاط
    # ---------------------------------------------------------
    path('azkar/mark/', AzkarMarkView.as_view(), name='azkar-mark'),

    # ---------------------------------------------------------
    # 6) تسجيل قراءة القرآن اليومية
    #    endpoint: POST /quran/read/
    #    الهدف: إضافة صفحات القرآن + حساب الختمة + النقاط
    # ---------------------------------------------------------
    path('quran/read/', QuranReadView.as_view(), name='quran-read'),

    # ---------------------------------------------------------
    # 7) عرض نسبة التقدم في الختمة الحالية
    #    endpoint: GET /quran/progress/
    #    الهدف: معرفة نسبة الختمة وعدد الختمات المنجزة
    # ---------------------------------------------------------
    path('quran/progress/', QuranProgressView.as_view(), name='quran-progress'),
 
    path('points/summary/', PointsSummaryView.as_view(), name='points-summary'),
]
