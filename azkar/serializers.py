from .models import Azkar,AzkarCategory
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

class AzkarSerializer(serializers.ModelSerializer):
    title_id = serializers.IntegerField(source="title.id", read_only=True)
    title = serializers.CharField(source="title.title", read_only=True)

    class Meta:
        model = Azkar
        fields = ['id', 'description', 'title_id', 'title']
        read_only_fields = ['id', 'title_id', 'title']


class CreateAzkarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Azkar
        fields = ['id','description']
        read_only_fields=['id']

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model=AzkarCategory
        fields=['id','title']
        read_only_fields = ['id']



class TitleWithAzkarSerializer(serializers.ModelSerializer):
    azkar=CreateAzkarSerializer(many=True,read_only=True)

    class Meta:
        model=AzkarCategory
        fields=['id','title','azkar']
