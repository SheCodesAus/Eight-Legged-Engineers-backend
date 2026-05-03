from rest_framework import serializers
from .models import Kid


class KidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kid
        fields = '__all__'
