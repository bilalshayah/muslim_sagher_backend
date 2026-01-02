from django.contrib import admin


# Register your models here.
from .models import Video

@admin.register(Video)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'video', 'is_lock','created_at')
    search_fields = ('title',)
    list_filter = ('created_at','is_lock')