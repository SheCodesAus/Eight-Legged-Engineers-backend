from rest_framework import serializers
from .models import Venue

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'

class VenueDetailSerializer(VenueSerializer):
    
    def update(self, instance, validated_data):
        instance.main_category = validated_data.get('main_category', instance.main_category)
        instance.sub_category = validated_data.get('sub_category', instance.sub_category)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.suburb = validated_data.get('suburb', instance.suburb)
        instance.opening_times = validated_data.get('opening_times', instance.opening_times)
        instance.min_age = validated_data.get('min_age', instance.min_age)
        instance.max_age = validated_data.get('max_age', instance.max_age)
        instance.cost = validated_data.get('cost', instance.cost)
        instance.kids_eat_free = validated_data.get('kids_eat_free', instance.kids_eat_free)
        instance.indoor_outdoor = validated_data.get('indoor_outdoor', instance.indoor_outdoor)
        instance.wheelchair_friendly = validated_data.get('wheelchair_friendly', instance.wheelchair_friendly)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.ratings_id = validated_data.get('ratings_id', instance.ratings_id)
        instance.save()
        return instance