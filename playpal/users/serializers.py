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


class KidsNestedSerializer(KidsSerializer):
    """Smaller read-only representation for nested usage."""
    class Meta(KidsSerializer.Meta):
        fields = ['id', 'birth_month', 'birth_year', 'created_at']
        read_only_fields = ['id',]


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer including nested kids."""
    kids = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'supabase_uid', 'kids']
        read_only_fields = ['supabase_uid']

    def get_kids(self, obj):
        qs = Kids.objects.filter(user=obj)
        return KidsNestedSerializer(qs, many=True).data
