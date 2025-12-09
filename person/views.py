from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Person
from .serializer import PersonSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
class RegisterView(generics.CreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    @swagger_auto_schema(
        operation_summary="Register new Person",
        operation_description="إضافة مستخدم جديد (طفل أو Admin)",
        tags=["Person"],
        responses={
            201: openapi.Response("User created successfully", PersonSerializer),
            400: "Validation Error"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Create your views here.


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Login",
        operation_description="تسجيل الدخول باستخدام الاسم وكلمة السر",
        tags=["Person"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'password'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="اسم المستخدم"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="كلمة المرور"),
            }
        ),
        responses={
            200: "Login successful",
            400: "Invalid name or password"
        }
    )
    def post(self, request):
        name = request.data.get("name")
        password = request.data.get("password")

        if not name or not password:
            return Response({"error": "Please provide name and password"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Person.objects.get(name=name)
        except Person.DoesNotExist:
            return Response({"error": "Invalid name or password"}, status=status.HTTP_400_BAD_REQUEST)

        # تحقق من كلمة السر
        if not check_password(password, user.password):
            return Response({"error": "Invalid name or password"}, status=status.HTTP_400_BAD_REQUEST)

        # توليد التوكن
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "message": "Login successful",
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "mobile": user.mobile,
            "tokens": {
                "access": str(access),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_200_OK)