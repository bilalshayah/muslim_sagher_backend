from rest_framework import serializers
from .models import Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'password', 'mobile', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')     # اسحب الباسورد
        user = Person(**validated_data)               # أنشئ المستخدم
        user.set_password(password)                   # 🔥 شفر الباسورد هنا
        user.save()
        return user
        