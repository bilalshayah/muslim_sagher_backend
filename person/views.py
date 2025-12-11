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
from .models import Person
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
            customer = Person.objects.get(name=name)
        except Person.DoesNotExist:
            return Response({"error": "Invalid name or password"}, status=status.HTTP_400_BAD_REQUEST)

        # تحقق من كلمة السر
        if password != customer.password:
             return Response({"error": "Invalid name or password"}, status=status.HTTP_400_BAD_REQUEST)

        # توليد التوكن
        # refresh = RefreshToken.for_user(user)
        # access = refresh.access_token
        refresh = RefreshToken()
        refresh['user_id'] =customer.id
        refresh['name'] =customer.name
        refresh['role'] =customer.role

        access = refresh.access_token

        return Response({
            "message": "Login successful",
            "id": customer.id,
            "name": customer.name,
            "role": customer.role,
            "mobile": customer.mobile,
            "tokens": {
                "access": str(access),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_200_OK)

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from .models import Person
# from .serializer import PersonSerializer
# from rest_framework_simplejwt.tokens import RefreshToken

# class PersonAuthView(APIView):
#     permission_classes = [AllowAny]
#     authentication_classes = []

#     @swagger_auto_schema(
#         operation_summary="Register or Login Person",
#         operation_description="يمكن التسجيل أو تسجيل الدخول باستخدام نفس الـ endpoint. ضع 'action':'register' أو 'login'",
#         request_body=PersonSerializer,
#         responses={
#             200: openapi.Response(
#                 description="Success",
#                 examples={
#                     "application/json": {
#                         "id": 1,
#                         "name": "ali",
#                         "mobile": "0912345678",
#                         "role": "customer",
#                         "token": "jwt_token_here"
#                     }
#                 }
#             ),
#             400: "Validation Error or Invalid name/password"
#         }
#     )
#     def post(self, request):
#         serializer = PersonSerializer(data=request.data)
#         if serializer.is_valid():
#             action = serializer.validated_data.get('action')

#             if action == 'register':
#                 person = serializer.save()  # إنشاء الحساب
#             elif action == 'login':
#                 person = serializer.validated_data.get('person')  # تم التحقق في validate()
#             else:
#                 return Response({"error": "Invalid action, must be 'register' or 'login'"},
#                                 status=status.HTTP_400_BAD_REQUEST)

#             # توليد توكن JWT
#             refresh = RefreshToken.for_user(person)
#             access = refresh.access_token

#             return Response({
#                 "id": person.id,
#                 "name": person.name,
#                 "mobile": person.mobile,
#                 "role": person.role,
#                 "tokens": {
#                     "access": str(access),
#                     "refresh": str(refresh)
#                 }
#             }, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
