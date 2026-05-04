import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class SupabaseAuthentication(BaseAuthentication):
    """
    Verifies a Supabase JWT from the Authorization: Bearer header.
    On first login, auto-creates a Django user linked to the Supabase account.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # No token — let permission classes decide if this is ok

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                audience='authenticated',
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        supabase_uid = payload.get('sub')
        email = payload.get('email', '')

        if not supabase_uid:
            raise AuthenticationFailed('Token missing user ID.')

        user = self._get_or_create_user(supabase_uid, email)
        return (user, token)

    def _get_or_create_user(self, supabase_uid, email):
        user, created = User.objects.get_or_create(
            supabase_uid=supabase_uid,
            defaults={
                'username': supabase_uid,
                'email': email,
            },
        )
        if not created and user.email != email:
            user.email = email
            user.save(update_fields=['email'])
        return user
