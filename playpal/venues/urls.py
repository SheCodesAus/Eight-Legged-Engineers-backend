from django.urls import path
from . import views

urlpatterns = [
    path('venues/', views.VenueList.as_view()),
    path('venues/<int:pk>/', views.VenueDetail.as_view()),
]