from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import AzkarCategory, Azkar


# -------------------------
# Inline: عرض الأذكار داخل صفحة الفئة
# -------------------------
class AzkarInline(admin.TabularInline):
    model = Azkar
    extra = 1  # عدد الحقول الفارغة لإضافة أذكار جديدة


# -------------------------
# Category Admin
# -------------------------
@admin.register(AzkarCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    inlines = [AzkarInline]  # عرض الأذكار داخل الفئة


# -------------------------
# Azkar Admin
# -------------------------
@admin.register(Azkar)
class AzkarAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'title')
    list_filter = ('title',)
    search_fields = ('description',)