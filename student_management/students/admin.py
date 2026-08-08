from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'course', 'age')
    search_fields = ('name', 'email', 'course')