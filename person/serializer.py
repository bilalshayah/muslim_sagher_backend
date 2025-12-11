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
        customer = Person(**validated_data)  
        customer.password = password              # أنشئ المستخدم
        # user.set_password(password)                   # 🔥 شفر الباسورد هنا
        customer.save()
        return customer
# from rest_framework import serializers
# from .models import Person

# class PersonSerializer(serializers.ModelSerializer):
#     action = serializers.CharField(write_only=True)  # 'register' أو 'login'

#     class Meta:
#         model = Person
#         fields = ['id', 'name', 'password', 'mobile', 'role', 'action']
#         extra_kwargs = {'password': {'write_only': True}}

#     def validate(self, data):
#         action = data.get('action')
#         name = data.get('name')
#         password = data.get('password')

#         if action == 'login':
#             try:
#                 person = Person.objects.get(name=name)
#             except Person.DoesNotExist:
#                 raise serializers.ValidationError("Invalid name or password")

#             if person.password != password:
#                 raise serializers.ValidationError("Invalid name or password")

#             data['person'] = person

#         return data

#     def create(self, validated_data):
#         # إذا التسجيل
#         validated_data.pop('action', None)
#         return Person.objects.create(**validated_data)
