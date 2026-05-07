from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Venue
from .serializers import VenueSerializer, VenueDetailSerializer

class VenueList(APIView):
    # Handles the list of all venues.
    # GET /api/venues/ Returns a list of all venues (excluding archived ones)
    # POST /api/venues/ Creates a new venue

    
    def get(self, request):
        # Get all venues that haven't been archived.
        venues = Venue.objects.filter(is_archived=False)
        # Serializer turns the venue objects into JSON the frontend can use
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Take the JSON data from the frontend and try to make a Venue out of it
        serializer = VenueSerializer(data=request.data)
        
        # is_valid() checks if the data is valid
        if serializer.is_valid():
            # If valid then thsis will save it to the database
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        # If invalid, send the errors back so the frontend knows what went wrong
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class VenueDetail(APIView):
    # Handles a single venue by its ID.
    # GET /api/venues/<id>/ Get one venues details
    # PATCH /api/venues/<id>/ Update some fields on the venue
    
    def get(self, request, pk):
        # pk = primary key (the venue's ID)
        venue = get_object_or_404(Venue, pk=pk)
        serializer = VenueDetailSerializer(venue)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        # Find the venue we want to update
        venue = get_object_or_404(Venue, pk=pk)
        
        # partial=True means we don't have to send every field, just the ones changing
        serializer = VenueDetailSerializer(
            instance=venue,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )