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
        operation_description="إنشاء حساب جديد.",
        responses={
            201: openapi.Response(
                description="تم إنشاء الحساب بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تم إنشاء الحساب بنجاح"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                "name": openapi.Schema(type=openapi.TYPE_STRING, example="أحمد"),
                                "mobile": openapi.Schema(type=openapi.TYPE_STRING, example="0999999999"),
                                # أضيفي أي حقول أخرى موجودة في RegisterSerializer
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="بيانات غير صحيحة",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="بيانات غير صحيحة"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
        },
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



# -----------------------------
# Login View
# -----------------------------
class LoginView(APIView):

    @swagger_auto_schema(
        operation_description="تسجيل دخول باستخدام رقم الهاتف + اسم الطفل.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="تم تسجيل الدخول بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تم تسجيل الدخول بنجاح"),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                            "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                                            "name": openapi.Schema(type=openapi.TYPE_STRING, example="أحمد"),
                                                            "mobile": openapi.Schema(type=openapi.TYPE_STRING, example="0999999999"),
                                                            "access": openapi.Schema(type=openapi.TYPE_STRING, example="jwt-access-token"),
                                                            "refresh": openapi.Schema(type=openapi.TYPE_STRING, example="jwt-refresh-token"),}
                                                                                                                                                    
                                     )
                                }
                                       )
            ),
            400: openapi.Response(
                description="بيانات غير صحيحة",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="بيانات غير صحيحة"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
        }
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
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="success"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="تم تحديث التوكن بنجاح"),
                        "data":openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "access": openapi.Schema(type=openapi.TYPE_STRING, example="new-access-token"),
                                                }
                                            )

                    }
                )
            ),
            401: openapi.Response(
                description="Refresh Token غير صالح أو منتهي",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, example="error"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Refresh Token غير صالح أو منتهي"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
        }
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





