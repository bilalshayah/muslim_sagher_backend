from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Story, StoryPage


# -----------------------------
# Inline لعرض صفحات القصة داخل صفحة القصة
# -----------------------------
class StoryPageInline(admin.TabularInline):
    model = StoryPage
    extra = 1  # عدد الصفحات الفارغة الجاهزة للإضافة
    fields = ("page_number", "image", "description")
    ordering = ("page_number",)


# -----------------------------
# Admin للقصة
# -----------------------------
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)
    inlines = [StoryPageInline]  # عرض الصفحات داخل القصة


# -----------------------------
# Admin للصفحات (اختياري)
# -----------------------------
@admin.register(StoryPage)
class StoryPageAdmin(admin.ModelAdmin):
    list_display = ("id", "story", "page_number")
    list_filter = ("story",)
    search_fields = ("story__title", "description")
    ordering = ("story", "page_number")