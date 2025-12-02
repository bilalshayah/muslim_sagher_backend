from django.urls import path
from .views import VideoCreateListView

urlpatterns = [
    path('videos/', VideoCreateListView.as_view(), name='video-list-create'),
]
