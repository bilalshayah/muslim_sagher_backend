from django.contrib import admin

# Register your models here.
from .models import Azkar

@admin.register(Azkar)
class ZikrAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title", "description")