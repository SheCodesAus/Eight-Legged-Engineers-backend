from django.contrib import admin
from .models import Venue

# This is the code for the admin portal.
# @admin.register(Venue) is where Django is bein told to add the venue model to the admin panel.

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('main_category','sub_category','address', 'suburb', 'opening_times','age_range', 'cost', 'kids_eat_free', 'indoor_outdoor', 'wheelchair_friendly', 'latitude', 'longitude', 'image_url', 'verify_before_launch', 'kids_eat_free')
    list_filter = ('main_category', 'sub_category', 'verify_before_launch')
    search_fields = ('address', 'suburb', 'sub_category')
    list_editable = ('verify_before_launch',)