from django.urls import path
from .views import AzkarListView,CreateAzkarView,UpdateAzkarView,DeleteAzkarView,ZikrDetailView

urlpatterns = [
    path('create/', CreateAzkarView.as_view(), name='create_azkar'),
    path('update/<int:pk>/', UpdateAzkarView.as_view(), name='update_azkar'),
    path('delete/<int:pk>/', DeleteAzkarView.as_view(), name='delete_azkar'),
    path('',AzkarListView.as_view(),name='azkar'),
    path('<int:pk>/',ZikrDetailView.as_view(),name='zikr'),
   


]