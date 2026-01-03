from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView

from utils.swagger import auto_swagger

from django.contrib.auth import get_user_model
from .serializer import RegisterSerializer, LoginSerializer

Person = get_user_model()


# -----------------------------
# Register View
# -----------------------------

class RegisterView(CreateAPIView):
    queryset = Person.objects.all()
    serializer_class = RegisterSerializer

    @auto_swagger(
        description="إنشاء حساب جديد",
        request_body=RegisterSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "status": "success",
                "message": "تم إنشاء الحساب بنجاح",
                "data": RegisterSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "بيانات غير صحيحة",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# # -----------------------------
# # Login View
# # -----------------------------
class LoginView(APIView):

    @auto_swagger(
        description="تسجيل دخول",
        request_body=LoginSerializer
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response({
                "status": "success",
                "message": "تم تسجيل الدخول بنجاح",
                "data": serializer.validated_data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "بيانات غير صحيحة",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# Refresh Token View
# -----------------------------
class CustomTokenRefreshView(TokenRefreshView):

    @auto_swagger(
        description="تحديث الـ Access Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=["refresh"]
        )
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            return Response({
                "status": "success",
                "message": "تم تحديث التوكن بنجاح",
                "data": response.data
            }, status=200)

        return Response({
            "status": "error",
            "message": "Refresh Token غير صالح أو منتهي",
            "data": response.data
        }, status=response.status_code)
