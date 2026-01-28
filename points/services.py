



from django.db import transaction
from django.utils import timezone
from .models import DailyActivity, UserPoints,DailyAzkarStatus,AzkarCategory,QuranProgress
from .prayer_utils import is_within_prayer_time


# ----------------------------------------------------
# جلب أو إنشاء سجل اليوم الحالي
# ----------------------------------------------------
def get_today_activity(user):
    today = timezone.localdate()
    activity, created = DailyActivity.objects.get_or_create(
        user=user,
        date=today,
        defaults={
            "fajr": False, "dhuhr": False, "asr": False, "maghrib": False, "isha": False,
            "taraweeh": False, "fasting": False,
            "sunnah_fajr": False, "sunnah_dhuhr": False,
            "sunnah_maghrib": False, "sunnah_isha": False,
            "quran_pages": 0,
            "daily_points": 0,
        }
    )
    if created or activity.azkar_status.count() == 0:
        for category in AzkarCategory.objects.all():
            DailyAzkarStatus.objects.get_or_create(
                activity=activity,
                category=category,
                defaults={"done": False}
            )

    return activity


# ----------------------------------------------------
# إضافة نقاط للرصيد الكلي
# ----------------------------------------------------
def add_points(user, points):
    user_points, _ = UserPoints.objects.get_or_create(user=user)
    user_points.total_points += points
    user_points.save()


# ----------------------------------------------------
# تسجيل صلاة مفروضة
# ----------------------------------------------------
@transaction.atomic
def mark_prayer(user, prayer_name):
    activity = get_today_activity(user)

    # إذا كانت الصلاة مسجلة مسبقًا → لا نقاط
    if getattr(activity, prayer_name):
        return activity, 0

    # التحقق من الوقت (حسب مواقيت دمشق)
    if not is_within_prayer_time(prayer_name):
        return activity, 0

    # نقاط الصلاة (يمكنك تعديلها)
    PRAYER_POINTS = 2

    setattr(activity, prayer_name, True)
    activity.daily_points += PRAYER_POINTS
    activity.save()

    add_points(user, PRAYER_POINTS)
    return activity, PRAYER_POINTS


# ----------------------------------------------------
# تسجيل صيام اليوم
# ----------------------------------------------------
@transaction.atomic
def mark_fasting(user):
    activity = get_today_activity(user)

    # إذا كان مسجل مسبقًا → لا نقاط
    if activity.fasting:
        return activity, 0

    FASTING_POINTS = 3

    activity.fasting = True
    activity.daily_points += FASTING_POINTS
    activity.save()

    add_points(user, FASTING_POINTS)
    return activity, FASTING_POINTS


# ----------------------------------------------------
# تسجيل سنة (الفجر – الظهر – المغرب – العشاء)
# ----------------------------------------------------
@transaction.atomic
def mark_sunnah(user, sunnah_name):
    activity = get_today_activity(user)

    field = f"sunnah_{sunnah_name}"

    # إذا مسجل مسبقًا → لا نقاط
    if getattr(activity, field):
        return activity, 0

    SUNNAH_POINTS = 1  # يمكنك تغييرها

    setattr(activity, field, True)
    activity.daily_points += SUNNAH_POINTS
    activity.save()

    add_points(user, SUNNAH_POINTS)
    return activity, SUNNAH_POINTS


# ----------------------------------------------------
# تسجيل التراويح
# ----------------------------------------------------
@transaction.atomic
def mark_taraweeh(user):
    activity = get_today_activity(user)

    if activity.taraweeh:
        return activity, 0

    TARAWEEH_POINTS = 5  # يمكنك تغييرها

    activity.taraweeh = True
    activity.daily_points += TARAWEEH_POINTS
    activity.save()

    add_points(user, TARAWEEH_POINTS)
    return activity, TARAWEEH_POINTS
# ----------------------------------------------------
# تسجيل الأذكار
# ----------------------------------------------------
@transaction.atomic
def mark_azkar(user, category_id):

    if not category_id:
        raise ValueError("category_id is required")

    today = timezone.localdate()

    # DailyActivity لليوم
    activity, _ = DailyActivity.objects.get_or_create(
        user=user,
        date=today
    )

    # DailyAzkarStatus للفئة المطلوبة
    status, created = DailyAzkarStatus.objects.get_or_create(
        activity=activity,
        category_id=category_id,
        defaults={"done": False}
    )

    # إذا كان منجزًا مسبقًا → لا نقاط
    if status.done:
        return activity, 0

    # تحديث الحالة
    status.done = True
    status.save()

    # إضافة النقاط
    POINTS = 2
    activity.daily_points += POINTS
    activity.save()

    # إضافة النقاط للمستخدم
    add_points(user, POINTS)

    return activity, POINTS
# ----------------------------------------------------
# تسجيل القرآن والختمات
# ----------------------------------------------------


@transaction.atomic
def mark_quran_reading(user, pages):
    today = timezone.localdate()

    # سجل اليوم
    activity, _ = DailyActivity.objects.get_or_create(
        user=user,
        date=today,
        defaults={"quran_pages": 0}
    )

    # تحديث صفحات اليوم
    activity.quran_pages += pages
    activity.daily_points += pages
    activity.save()

    # تقدم الختمة
    progress, _ = QuranProgress.objects.get_or_create(user=user)

    progress.total_pages_read += pages
    progress.current_khatma_pages += pages

    reward = 0

    # 🔥 إذا اكتملت الختمة الحالية
    if progress.current_khatma_pages >= 604:

        # مكافأة الختمة (مرة واحدة فقط)
        if not progress.reward_given_for_current_khatma:
            reward = 50
            progress.reward_given_for_current_khatma = True

        # زيادة عداد الختمات
        progress.completed_khatmas += 1

        # إعادة ضبط الختمة الحالية
        progress.current_khatma_pages -= 604  # لو قرأ أكثر من 604
        progress.reward_given_for_current_khatma = False

    progress.save()

    # تحديث النقاط الكلية
    user_points, _ = UserPoints.objects.get_or_create(user=user)
    user_points.total_points += pages + reward
    user_points.save()

    return activity, progress, pages, reward
# ----------------------------------------------------
# تفصيل النقاط 
# ----------------------------------------------------
from .models import DailyActivity, UserPoints

def get_points_summary(user):
    """
    خدمة لحساب النقاط الكلية + تفصيل النقاط حسب النشاط.
    لا تُرجع أي تفاصيل يومية، فقط مجموع النقاط.
    """

    activities = DailyActivity.objects.filter(user=user)

    prayers_points = 0
    sunnah_points = 0
    fasting_points = 0
    taraweeh_points = 0
    quran_points = 0
    azkar_points = 0

    for a in activities:
        # الصلوات الخمس
        prayers_points += (a.fajr + a.dhuhr + a.asr + a.maghrib + a.isha) * 2

        # السنن
        sunnah_points += (
            a.sunnah_fajr +
            a.sunnah_dhuhr +
            a.sunnah_maghrib +
            a.sunnah_isha
        ) * 1

        # الصيام
        fasting_points += 3 if a.fasting else 0

        # التراويح
        taraweeh_points += 5 if a.taraweeh else 0

        # القرآن
        quran_points += a.quran_pages * 1

        # الأذكار
        azkar_points += a.azkar_status.filter(done=True).count() * 2

    # إجمالي النقاط من DailyActivity
    total_from_activities = (
        prayers_points +
        sunnah_points +
        fasting_points +
        taraweeh_points +
        quran_points +
        azkar_points
    )

    # النقاط الكلية من UserPoints
    user_points, _ = UserPoints.objects.get_or_create(user=user)

    return {
        "total_points": user_points.total_points,
        "breakdown": {
            "prayers": prayers_points,
            "sunnah": sunnah_points,
            "fasting": fasting_points,
            "taraweeh": taraweeh_points,
            "quran": quran_points,
            "azkar": azkar_points,
        }
    }