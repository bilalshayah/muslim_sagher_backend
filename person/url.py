from django.urls import path
from .views import RegisterView, LoginView,TokenRefreshView,ForgotPasswordView,ResetPassowrdView,ProfileUpdateView,ProfileView,LogoutView,SaveDeviceTokenView
# from .views import PersonAuthView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forget-password/',ForgotPasswordView.as_view(),name='forgot_password'),
    path('reset-password/',ResetPassowrdView.as_view(),name='reset_password'),
    path('profile/',ProfileView.as_view(),name='profile'),
    path('profile/update/',ProfileUpdateView.as_view(),name='profile_update'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path("save-device-token/", SaveDeviceTokenView.as_view(), name="save-device-token"),


]

 