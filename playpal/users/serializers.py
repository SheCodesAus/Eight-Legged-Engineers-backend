from rest_framework import serializers
from django.utils import timezone
from .models import CustomUser, Kids


class KidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kids
        fields = ['id', 'birth_month', 'birth_year', 'user']
        read_only_fields = ['user']

    ## Ensure that kid's maximum age is 12 at any given time.
    def validate_birth_year(self, value):
        min_year = timezone.now().year - 12
        if value < min_year:
            raise serializers.ValidationError(f"Birth year must be {min_year} or later.")
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    kids = KidsSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'supabase_uid', 'is_staff', 'is_superuser','kids']
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
        fields = ['id', 'email', 'username', 'supabase_uid', 'is_staff', 'is_superuser', 'kids']
        read_only_fields = ['supabase_uid', 'is_staff', 'is_superuser']

    def get_kids(self, obj):
        qs = Kids.objects.filter(user=obj)
        return KidsNestedSerializer(qs, many=True).data
