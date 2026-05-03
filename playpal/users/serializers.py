from rest_framework import serializers
from .models import CustomUsers, Kids

class CustomUserSerializer(serializers.ModelSerializer):

    ## treat supabase_uid and is_supeuser as read only attributes
    supabase_uid = serializers.ReadOnlyField()
    is_superuser = serializers.ReadOnlyField()
    class Meta:
        ## grab the CustomUser Model
        model = CustomUsers
        ## show all fields except for the email attribute
        exclude = ('email',)
        extra_kwargs = {'password': {'write_only': True}} #kwargs = keyword arguments, this means we are passing passwords are write only. we are going to be gonna be accepting passwords in and not sending passwords out to the API for security risks.

class KidsSerializer(serializers.ModelSerializer):
    
     ## treat user_id as read only attributes
    user_id = serializers.ReadOnlyField()
    class Meta:
        ## grab the Kids model
        model = Kids
      
## add nested serializer of one user with their kids

class CustomUserDetailSerializer(CustomUserSerializer):

    ## return the user's kids
    kids = KidsSerializer(many=True, read_only=True)