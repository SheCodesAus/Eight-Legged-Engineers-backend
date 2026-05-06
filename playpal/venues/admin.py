from django.contrib import admin
from .models import Venue

# This is the code for the admin portal.
# @admin.register(Venue) is where Django is bein told to add the venue model to the admin panel.

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_category', 'suburb', 'main_category', 'is_published', 'is_archived', 'kids_eat_free')
    list_filter = ('main_category', 'sub_category', 'is_published', 'is_archived', 'indoor_outdoor')
    search_fields = ('name', 'address', 'suburb', 'sub_category')
    list_editable = ('is_published', 'is_archived')