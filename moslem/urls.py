"""
URL configuration for moslem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static


schema_view = get_schema_view(
   openapi.Info(
      title="Muslim Sagher API",
      default_version='v1',
      description="API documentation for Muslim Sagher Backend",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@muslimsagher.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/video/', include('video.url')),
    path('api/persons/', include('person.url')),
    path('api/quiz/', include('quiz.urls')),
    path('api/azkar-category/', include('azkar.urls')),
    path('api/points/',include('points.urls')),
    path("api/", include("stories.urls")),
    
    

    
    # Swagger/Redoc URLs
path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

