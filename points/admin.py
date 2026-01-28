from django.contrib import admin

# Register your models here.
from .models import DailyActivity, UserPoints, QuranProgress


# ---------------------------------------------------------
# 1) DailyActivity Admin
# ---------------------------------------------------------
@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'date',
        'fajr', 'dhuhr', 'asr', 'maghrib', 'isha',
        'sunnah_fajr', 'sunnah_dhuhr', 'sunnah_maghrib', 'sunnah_isha',
        'taraweeh', 'fasting',
        'quran_pages',
        'daily_points'
    )

    list_filter = (
        'date',
        'fasting',
        'taraweeh',
        'fajr', 'dhuhr', 'asr', 'maghrib', 'isha',
    )

    search_fields = ('user__username',)

    ordering = ('-date',)


# ---------------------------------------------------------
# 2) UserPoints Admin
# ---------------------------------------------------------
@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'last_updated')
    search_fields = ('user__username',)
    ordering = ('-total_points',)


# ---------------------------------------------------------
# 3) QuranProgress Admin
# ---------------------------------------------------------
@admin.register(QuranProgress)
class QuranProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'total_pages_read',
        'completed_khatmas',
        'current_khatma_pages',
        'reward_given_for_current_khatma'
    )

    search_fields = ('user__username',)

    list_filter = ('completed_khatmas',)

    ordering = ('-completed_khatmas', '-total_pages_read')