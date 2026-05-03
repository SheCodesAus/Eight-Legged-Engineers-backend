from django.contrib import admin
from .models import Kid


@admin.register(Kid)
class KidAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'birth_year', 'birth_month')
    list_filter = ('birth_year', 'birth_month')
    search_fields = ('user__username',)
