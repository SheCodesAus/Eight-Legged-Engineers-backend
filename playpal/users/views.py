import json
import hmac
import hashlib

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.conf import settings

from .models import CustomUser, Kids
from .serializers import CustomUserSerializer, KidsSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing CustomUsers.
    GET /api/users/me/ - Get own profile (authenticated)
    PATCH /api/users/me/ - Update own profile (authenticated)
    """
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]  # no unauthenticated reads

    def get_queryset(self):
        # Regular users only see themselves; admins see all
        if self.request.user.is_staff:
            return CustomUser.objects.prefetch_related('kids').all()
        return CustomUser.objects.prefetch_related('kids').filter(pk=self.request.user.pk)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """
        GET  /api/users/me/ - return own profile
        PATCH /api/users/me/ - update own profile
        """
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class KidsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Kids.
    GET /api/kids/ - List own kids only
    POST /api/kids/ - Create a kid
    """
    serializer_class = KidsSerializer
    permission_classes = [IsAuthenticated]  # tightened from IsAuthenticatedOrReadOnly

    def get_queryset(self):
        # Scope kids to the authenticated user only
        return Kids.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class SupabaseWebhookView(APIView):
    """
    POST /api/auth/webhook/
    Receives Supabase auth events and syncs users into Django.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Optional: verify webhook secret from Supabase
        # Add SUPABASE_WEBHOOK_SECRET to your settings.py
        secret = getattr(settings, 'SUPABASE_WEBHOOK_SECRET', None)
        if secret:
            sig = request.headers.get('x-webhook-secret', '')
            if not hmac.compare_digest(sig, secret):
                return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        event_type = payload.get('type')  # INSERT, UPDATE, DELETE
        record = payload.get('record', {})

        if event_type == 'INSERT':
            self._handle_signup(record)
        elif event_type == 'UPDATE':
            self._handle_update(record)
        elif event_type == 'DELETE':
            self._handle_delete(payload.get('old_record', {}))

        return JsonResponse({'status': 'ok'})

    def _handle_signup(self, record):
        email = record.get('email')
        supabase_uid = record.get('id')
        if email and supabase_uid:
            CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'supabase_uid': supabase_uid,  # add this field to your model if not present
                }
            )

    def _handle_update(self, record):
        email = record.get('email')
        supabase_uid = record.get('id')
        if supabase_uid:
            CustomUser.objects.filter(supabase_uid=supabase_uid).update(email=email)

    def _handle_delete(self, old_record):
        supabase_uid = old_record.get('id')
        if supabase_uid:
            CustomUser.objects.filter(supabase_uid=supabase_uid).delete()