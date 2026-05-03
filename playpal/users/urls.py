
from django.urls import path
from . import views

## formatting URLs with views from views.py
urlpatterns = [
    path('users/', views.CustomUsersList.as_view()),
    path('users/<int:pk>/', views.CustomUsersDetailsList.as_view()),
    path('kids/', views.KidsList.as_view()),
    path('kids/<int:pk>/', views.KidsDetail.as_view()),
]