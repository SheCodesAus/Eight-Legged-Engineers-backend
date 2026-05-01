from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Venue
from .serializers import VenueSerializer

class VenueView(viewsets.ReadOnlyModelViewSet):
# Which rows should we fetch from the database - this is saying lets filter out sites not verified.
    queryset = Venue.objects.filter(verify_before_launch=False)
    serializer_class = VenueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
# Which fields users could filter with.
    filterset_fields = ['main_category', 'sub_category', 'suburb', 'indoor_outdoor', 'age_range', 'cost']
# Which fields users can search against
    search_fields = ['suburb', 'sub_category']
