from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth import get_user_model
from .serializer import RegisterSerializer, LoginSerializer

Person = get_user_model()


# -----------------------------
# Register View
# -----------------------------
class RegisterView(CreateAPIView):
    queryset = Person.objects.all()
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="إنشاء حساب طفل جديد.",
        responses={
            201: openapi.Response(
                description="تم إنشاء الحساب بنجاح",
                schema=RegisterSerializer
            ),
            400: "بيانات غير صحيحة"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# -----------------------------
# Login View
# -----------------------------
class LoginView(APIView):

    @swagger_auto_schema(
        operation_description="تسجيل دخول طفل باستخدام رقم الهاتف + اسم الطفل + كلمة المرور.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="تم تسجيل الدخول بنجاح",
                schema=LoginSerializer
            ),
            400: "بيانات غير صحيحة"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# Refresh Token View
# -----------------------------
class CustomTokenRefreshView(TokenRefreshView):

    @swagger_auto_schema(
        operation_description="تحديث الـ Access Token باستخدام Refresh Token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Refresh Token الذي تم الحصول عليه أثناء تسجيل الدخول"
                ),
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="تم تحديث الـ Access Token بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: "Refresh Token غير صالح أو منتهي"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)





