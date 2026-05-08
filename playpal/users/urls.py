from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, KidsViewSet, SupabaseWebhookView

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'kids', KidsViewSet, basename='kids')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/webhook/', SupabaseWebhookView.as_view()),
]