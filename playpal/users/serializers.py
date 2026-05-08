from rest_framework import serializers
from .models import CustomUser, Kids


class KidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kids
        fields = ['id', 'birth_month', 'birth_year', 'user']
        read_only_fields = ['user']


class CustomUserSerializer(serializers.ModelSerializer):
    kids = KidsSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'supabase_uid', 'kids']
        read_only_fields = ['supabase_uid']
