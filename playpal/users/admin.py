from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_superuser',)

admin.site.register(CustomUser, CustomUserAdmin)