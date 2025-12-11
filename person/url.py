from django.urls import path
from .views import RegisterView, LoginView
# from .views import PersonAuthView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]
# urlpatterns = [
#     path('auth/', PersonAuthView.as_view(), name='person-auth'),
# ]
 
 