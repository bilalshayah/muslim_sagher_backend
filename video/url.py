from django.urls import path
from .views import (
    VideoCreateView,
    VideoUpdateView,
    VideoDeleteView,
    MyVideosView,
    VideoPlayView
)

urlpatterns = [
    path('create/', VideoCreateView.as_view(), name='video-create'),
    path('update/<int:pk>/', VideoUpdateView.as_view(), name='video-update'),
    path('delete/<int:pk>/', VideoDeleteView.as_view(), name='video-delete'),
    path('my-videos/', MyVideosView.as_view(), name='my-videos'),
    path("<int:pk>/play/", VideoPlayView.as_view(), name="video-play"),  #
]