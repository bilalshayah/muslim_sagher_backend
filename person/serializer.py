from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

Person = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    father_name = serializers.CharField(required=False, allow_null=True)
    mother_name = serializers.CharField(required=False, allow_null=True)
    birth_date = serializers.DateField(required=False,allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True,default=None)

    class Meta:
        model = Person
        fields = ['id', 'name', 'mobile', 'password', 'role','email','father_name','mother_name','birth_date']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_mobile(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("رقم الهاتف يجب أن يحتوي على أرقام فقط")
        if len(value) != 10:
            raise serializers.ValidationError("رقم الهاتف يجب أن يكون 10 أرقام")
        if not value.startswith("09"):
            raise serializers.ValidationError("رقم الهاتف يجب أن يبدأ بـ 09")
        return value

    def validate(self, data):
        if Person.objects.filter(name=data['name'], mobile=data['mobile']).exists():
            raise serializers.ValidationError("هذا الطفل مسجل مسبقًا")
        return data

    def create(self, validated_data):
        username = f"user_{uuid.uuid4().hex[:8]}"

        user = Person(
            username=username,
            name=validated_data['name'],
            mobile=validated_data['mobile'],
            role=validated_data['role'],
            father_name=validated_data.get('father_name'),
            mother_name=validated_data.get('mother_name'),
            email=validated_data.get('email'),
            birth_date=validated_data.get('birth_date')

        )
        user.set_password(validated_data['password'])
        user.save()

        return user
    

class LoginSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    mobile = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        full_name = data.get('full_name')
        mobile = data.get('mobile')
        password = data.get('password')

        try:
            user = Person.objects.get(mobile=mobile, name=full_name)
        except Person.DoesNotExist:
            raise serializers.ValidationError("لا يوجد مستخدم بهذه المعلومات")

        if not user.check_password(password):
            raise serializers.ValidationError("كلمة المرور غير صحيحة")

        refresh = RefreshToken.for_user(user)
        self.context["user"] = user
        return {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class ForgotPasswordSerializer(serializers.Serializer):
    name=serializers.CharField()
    mobile=serializers.CharField()

    def validate(self,data):
        name=data["name"]
        mobile=data["mobile"]
        
        if not Person.objects.filter(name=name,mobile=mobile).exists():
            raise serializers.ValidationError("لا يوجد مستخدم بهذه البيانات")

        return data
    
class ResetPasswordSerializer(serializers.Serializer):

    new_password=serializers.CharField()
    confirm_password=serializers.CharField()

    def validate(self,data):
        

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("كلمتا السر غير متطابقتين")
        
        return data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Person
        fields=['id','name','mobile','father_name','mother_name','email','birth_date']
        read_only_fields=['id']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            "email",
            "father_name",
            "mother_name",
            "birth_date",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "father_name": {"required": False},
            "mother_name": {"required": False},
            "birth_date": {"required": False},
        }


class DeviceTokenSerializer(serializers.Serializer):
    device_token = serializers.CharField()