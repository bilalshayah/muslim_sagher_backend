from rest_framework import serializers
from .models import DailyActivity, UserPoints


# ---------------------------------------------------------
# 1) Daily Activity Serializer
# ---------------------------------------------------------
class DailyActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyActivity
        fields = [
            'id', 'date',
            'fajr', 'dhuhr', 'asr', 'maghrib', 'isha',
            'taraweeh', 'fasting',
            'sunnah_fajr', 'sunnah_dhuhr', 'sunnah_maghrib', 'sunnah_isha',
            'quran_pages','daily_points',

        ]
        read_only_fields = ['date','daily_points']


class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = ['total_points', 'last_updated']

class PointsBreakdownSerializer(serializers.Serializer):
    prayers = serializers.IntegerField()
    taraweeh = serializers.IntegerField()
    fasting = serializers.IntegerField()
    sunnah = serializers.IntegerField()
    quran = serializers.IntegerField()
    azkar = serializers.IntegerField()
    total = serializers.IntegerField()

