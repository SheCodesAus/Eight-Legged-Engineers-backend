from rest_framework import serializers
from .models import Venue

# The essentially translates the venues into a JSON

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'