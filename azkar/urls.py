from django.urls import path
from .views import TitleListView,TitleDetailView,CreateAzkarView,CreateTitleView,UpdateAzkarView,UpdateTitleView,DeleteAzkarView,DeleteTitleView

urlpatterns = [
   path("", TitleListView.as_view()),
    path("<int:pk>/", TitleDetailView.as_view()),
    path("create/", CreateTitleView.as_view()),
    path("update/<int:pk>/", UpdateTitleView.as_view(), name="category-update"),
    path("delete/<int:pk>/", DeleteTitleView.as_view(), name="category-delete"),
    path("<int:pk>/zikr/create/", CreateAzkarView.as_view()),
    path("zikr/update/<int:pk>/", UpdateAzkarView.as_view()),
    path("zikr/delete/<int:pk>/", DeleteAzkarView.as_view()),
]