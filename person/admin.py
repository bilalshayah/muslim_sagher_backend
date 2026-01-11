from django.contrib import admin

# Register your models here.
from .models import Person

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mobile', 'username', 'role','mother_name','father_name','birth_date','email')
    search_fields = ('name', 'mobile', 'username')