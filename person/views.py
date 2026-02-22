from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from utils.swagger import auto_swagger
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from .serializer import RegisterSerializer, LoginSerializer,ForgotPasswordSerializer,ResetPasswordSerializer,ProfileSerializer,ProfileUpdateSerializer
from utils.notifications import send_firebase_notification
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
        description="تسجيل دخول + حفظ device token إن وُجد",
        request_body=LoginSerializer
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={})

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "بيانات غير صحيحة",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ المستخدم المستخرج من serializer
        user = serializer.context["user"]

        # ✅ حفظ device token إن أُرسل
        device_token = request.data.get("device_token")
        if device_token:
            user.device_token = device_token
            user.save(update_fields=["device_token"])

        # 🔔 إشعار ترحيبي (اختياري)
        if user.device_token:
            send_firebase_notification(
                user.device_token,
                "مرحبًا بعودتك 👋",
                "تم تسجيل دخولك بنجاح"
            )

        return Response({
            "status": "success",
            "message": "تم تسجيل الدخول بنجاح",
            "data": serializer.validated_data
        }, status=status.HTTP_200_OK)
# -----------------------------s
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


class ForgotPasswordView(APIView):
    @auto_swagger(
        description= "طلب استعادة تعيين كلمة السر بعد التحقق من اسم المستخدم ورقم الهاتف",
        request_body=ForgotPasswordSerializer,
        
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():

            reset_token = str(uuid.uuid4())

        # تخزين التوكن في session
            request.session["reset_token"] = reset_token
            request.session["reset_user"] = serializer.validated_data["name"]
            request.session["reset_user_mobile"] = serializer.validated_data["mobile"]

            return Response({
                "status": "success",
                "message": "يمكنك الآن إدخال كلمة السر الجديدة",
                "data": {"reset_token": reset_token}
            }, status=200)
        return Response({
            "status": "error",
            "message": "بيانات غير صحيحة",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class ForgotPasswordView(APIView):

    @auto_swagger(
        description="طلب استعادة كلمة المرور عبر التحقق من الاسم ورقم الهاتف",
        request_body=ForgotPasswordSerializer
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            # إنشاء reset token
           

            # تخزين التوكن في الـ session
            request.session["reset_allowed"] = True
            request.session["reset_name"] = serializer.validated_data["name"]
            request.session["reset_mobile"] = serializer.validated_data["mobile"]

            return Response({
                "status": "success",
                "message": "تم التحقق من البيانات ويمكنك الآن إدخال كلمة السر الجديدة",
                "data": {}
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "بيانات غير صحيحة",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPassowrdView(APIView):
    @auto_swagger(
        description="تغيير كلمة السر باستخدام reset_token",
        request_body=ResetPasswordSerializer
    )
    def post(self,request):
        
        if not request.session.get("reset_allowed"):
            return Response({
                "status": "error",
                "message": "لا يوجد طلب استعادة كلمة مرور فعال",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            name = request.session.get("reset_name")
            mobile = request.session.get("reset_mobile")

            try:
                user = Person.objects.get(name=name, mobile=mobile)
            except Person.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "المستخدم غير موجود",
                    "data": {}
                }, status=status.HTTP_404_NOT_FOUND)

            # تغيير كلمة السر
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # حذف حالة الاستعادة من الـ session
            request.session.pop("reset_allowed", None)
            request.session.pop("reset_name", None)
            request.session.pop("reset_mobile", None)

            return Response({
                "status": "success",
                "message": "تم تغيير كلمة السر بنجاح",
                "data": {}
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "بيانات غير صحيحة",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes=[IsAuthenticated]

    @auto_swagger(
        description="عرض بيانات البروفايل",
        responses={200:ProfileSerializer}   
    )
    def get(self,request):
        serializer=ProfileSerializer(request.user)
        return Response({
            "status":"success",
            "message":"تم جلب بيانات البروفايل",
            "data":serializer.data,
            },status=status.HTTP_200_OK
        )

class ProfileUpdateView(APIView):
    permission_classes=[IsAuthenticated]

    @auto_swagger(
        description="تعديل بيانات البروفايل",
        request_body=ProfileUpdateSerializer,
        responses={200:ProfileSerializer}
    ) 
    def put(self,request):
        serializer=ProfileUpdateSerializer(request.user,request.data,partial=True)     
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status":"success",
                "message":"تم تعديل بيانات البروفايل",
                "data":serializer.data}
            ,status=status.HTTP_200_OK)
        return Response({
            "status":"error",
            "message":"بيانات غير صحيحة",
            "data":serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes=[IsAuthenticated]

    @auto_swagger(
        description="تسجيل خروج المستخدم",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"refresh":openapi.Schema(type=openapi.TYPE_STRING)},
            required=['refresh']
        ))
    
    def post(self,request):
        try:
            refresh_token=request.data.get("refresh")
            token=RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "status":"success",
                "message":"تم تسجيل الخروج بنجاح",
                "data":{}
            },status=status.HTTP_200_OK)
        except:
            return Response({
                "status":"error",
                "message":"Refresh Token غير صالح",
                "data":{}
            },status=status.HTTP_400_BAD_REQUEST)


