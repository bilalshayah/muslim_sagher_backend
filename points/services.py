



from django.db import transaction
from django.utils import timezone
from .models import DailyActivity, UserPoints,DailyAzkarStatus,AzkarCategory,QuranProgress,OfflinePointEvent
from .prayer_utils import is_within_prayer_time
from utils.notifications import send_firebase_notification
from person.models import Person

# ----------------------------------------------------
# جلب أو إنشاء سجل اليوم الحالي
# ----------------------------------------------------
from django.utils import timezone
from django.db import transaction
from .models import DailyActivity, DailyAzkarStatus, AzkarCategory


@transaction.atomic
def get_today_activity(user):
    today = timezone.localdate()

    activity, created = DailyActivity.objects.get_or_create(
        user=user,
        date=today,
        defaults={
            "fajr": False,
            "dhuhr": False,
            "asr": False,
            "maghrib": False,
            "isha": False,
            "taraweeh": False,
            "fasting": False,
            "sunnah_fajr": False,
            "sunnah_dhuhr": False,
            "sunnah_maghrib": False,
            "sunnah_isha": False,
            "quran_pages": 0,
            "daily_points": 0,
        },
    )

    if created:
        categories = AzkarCategory.objects.all()
        DailyAzkarStatus.objects.bulk_create([
            DailyAzkarStatus(activity=activity, category=cat, done=False)
            for cat in categories
        ])

    return activity



# ----------------------------------------------------
# إضافة نقاط للرصيد الكلي
# ----------------------------------------------------

@transaction.atomic
def add_points(user, points: int):
    if points <= 0:
        return

    user_points = UserPoints.objects.select_for_update().get(
        user=user
    )

    user_points.total_points += int(points)
    user_points.save()
    if user.device_token:
        send_firebase_notification(
            user.device_token,
            "نقاط جديدة!",
            f"لقد حصلت على {points} نقاط جديدة"
        )

    return user_points.total_points



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

    # new_rewards = 
    add_points(user, PRAYER_POINTS)
    


    return activity, PRAYER_POINTS#,new_rewards


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

    # new_rewards=
    add_points(user, FASTING_POINTS)
    

    return activity, FASTING_POINTS#,new_rewards


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

    # new_rewards=
    add_points(user, SUNNAH_POINTS)
    

    return activity, SUNNAH_POINTS#,new_rewards


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

    # new_rewards=
    add_points(user, TARAWEEH_POINTS)
    

    return activity, TARAWEEH_POINTS#,new_rewards
# ----------------------------------------------------
# تسجيل الأذكار
# ----------------------------------------------------
@transaction.atomic
def mark_azkar(user, category_id):

    if not category_id:
        raise ValueError("category_id is required")

    today = timezone.localdate()

    # DailyActivity لليوم
    activity = get_today_activity(user)

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
    #new_rewards=
    add_points(user, POINTS)
    

    return activity, POINTS#,new_rewards
# ----------------------------------------------------
# تسجيل القرآن والختمات
# ----------------------------------------------------


@transaction.atomic
def mark_quran_reading(user, pages):
    today = timezone.localdate()

    # سجل اليوم
    activity = get_today_activity(user)

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
    add_points(user,pages+reward)
    if reward > 0:
        user_points = UserPoints.objects.get(user=user)
        user_points.khatma_reward_points += reward
        user_points.save()

    #new_rewards = check_and_unlock_rewards(user)

    return activity, progress, pages, reward#,new_rewards
# ----------------------------------------------------
# تفصيل النقاط 
# ----------------------------------------------------
# points/services.py

from .models import DailyActivity, UserPoints, OfflinePointEvent

def get_points_summary(user):
    activities = DailyActivity.objects.filter(user=user)
    offline_events = OfflinePointEvent.objects.filter(user=user)

    prayers_points = 0
    sunnah_points = 0
    fasting_points = 0
    taraweeh_points = 0
    quran_points = 0
    azkar_points = 0

    # -------- online (DailyActivity) --------
    for a in activities:
        prayers_points += (
            a.fajr + a.dhuhr + a.asr + a.maghrib + a.isha
        ) * 2

        sunnah_points += (
            a.sunnah_fajr +
            a.sunnah_dhuhr +
            a.sunnah_maghrib +
            a.sunnah_isha
        ) * 1

        fasting_points += 3 if a.fasting else 0
        taraweeh_points += 5 if a.taraweeh else 0
        quran_points += a.quran_pages
        azkar_points += a.azkar_status.filter(done=True).count() * 2

    # -------- offline --------
    offline_breakdown = {
        "prayers": 0,
        "sunnah": 0,
        "fasting": 0,
        "taraweeh": 0,
        "quran": 0,
        "azkar": 0,
    }

    for e in offline_events:
        offline_breakdown[e.event_type] += e.points

    # -------- totals --------
    user_points = UserPoints.objects.get(user=user)

    return {
        "total_points": user_points.total_points,
        "breakdown": {
            "prayers": prayers_points + offline_breakdown["prayers"],
            "sunnah": sunnah_points + offline_breakdown["sunnah"],
            "fasting": fasting_points + offline_breakdown["fasting"],
            "taraweeh": taraweeh_points + offline_breakdown["taraweeh"],
            "quran": quran_points + offline_breakdown["quran"],
            "azkar": azkar_points + offline_breakdown["azkar"],
            "points_spent_on_videos": user_points.points_spent_on_videos,
            "points_from_exams": user_points.points_from_exams,
            "khatma_reward_points": user_points.khatma_reward_points,

        }
    }


#---------------------------------------------------------
#نظام خاص بالمكافآت
#---------------------------------------------------------
from .models import UserReward

def user_owns_video(user, video_id):
    return UserReward.objects.filter(
        user=user,
        reward__video_id=video_id
    ).exists()


from .models import Reward, UserReward, UserPoints


def get_rewards_status_for_user(user):
    """
    ترجع جميع المكافآت مع حالتها بالنسبة للمستخدم:
    - owned
    - able
    - disabled
    """

    user_points= UserPoints.objects.get(user=user)
    owned_rewards_ids = set(
        UserReward.objects.filter(user=user)
        .values_list("reward_id", flat=True)
    )

    rewards = Reward.objects.filter(is_active=True)

    result = []

    for reward in rewards:
        if reward.id in owned_rewards_ids:
            status = "owned"
        elif user_points.total_points >= reward.cost_points:
            status = "able"
        else:
            status = "disabled"

        result.append({
            "id": reward.id,
            "title": reward.title,
            "type": reward.type,
            "cost_points": reward.cost_points,
            "status": status,
        })

    return result



@transaction.atomic
def unlock_reward_for_user(user, reward_id):
    reward = Reward.objects.select_for_update().get(
        id=reward_id,
        is_active=True
    )

    user_points = UserPoints.objects.select_for_update().get(user=user)

    # هل يملكها؟
    if UserReward.objects.filter(user=user, reward=reward).exists():
        return {
            "status": "owned",
            "points": user_points.total_points
        }

    # هل يملك نقاط كافية؟
    if user_points.total_points < reward.cost_points:
        return {
            "status": "not_enough_points",
            "points": user_points.total_points
        }

    # خصم النقاط
    user_points.total_points -= reward.cost_points
    user_points.points_spent_on_videos += reward.cost_points
    user_points.save()
    if user.device_token:
        send_firebase_notification(
            user.device_token,
            "تم الحسم من نقاطك",
            f"لقد حصلت على {reward.cost_points} نقاط جديدة"
        )

    # تسجيل المكافأة
    UserReward.objects.create(user=user, reward=reward)

    return {
        "status": "unlocked",
        "points": user_points.total_points
    }

def get_video_status(user, video):
    # إذا لا يوجد مكافأة → مقفل
    if not hasattr(video, "reward"):
        return "disabled"

    # إذا تم الشراء
    if UserReward.objects.filter(
        user=user,
        reward__video=video
    ).exists():
        return "owned"

    user_points = UserPoints.objects.get(user=user)

    if user_points.total_points >= video.reward.cost_points:
        return "able"

    return "disabled"


ALLOWED_TYPES = {
    "prayer",
    "fasting",
    "quran",
    "azkar",
    "sunnah",
    "taraweeh",
}

@transaction.atomic
def add_offline_event(user, event_type: str, points: int):
    if event_type not in ALLOWED_TYPES:
        raise ValueError("نوع الحدث غير مدعوم")

    if points <= 0:
        raise ValueError("عدد النقاط غير صالح")
    #اذا كان الحدث صيام يتم حسابها بالدالة من اجل اكتمال الختمة وجائزة الختمة تحسب
    if event_type == "quran":
        mark_quran_reading(user, points)
        user_points = UserPoints.objects.get(user=user)
    else:

    # 1️⃣ زيادة النقاط الكلية (الحقيقة)
        user_points= UserPoints.objects.select_for_update().get(
            user=user
        )
        user_points.total_points += points
        user_points.save()
        if user.device_token:
            send_firebase_notification(
            user.device_token,
            "نقاط جديدة!",
            f"لقد حصلت على {points} نقاط جديدة"
        )


    # 2️⃣ تسجيل الحدث فقط للتفصيل (breakdown)
    OfflinePointEvent.objects.create(
        user=user,
        event_type=event_type,
        points=points
    )

    return user_points.total_points