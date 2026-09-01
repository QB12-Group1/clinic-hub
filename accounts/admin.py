from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    
    list_display = ("username","role",)
    list_filter = ("role",)
    search_fields = ("username",)
    ordering = ("-date_joined",)
    