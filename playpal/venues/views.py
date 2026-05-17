from rest_framework import request, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Venue, Rating
from .serializers import VenueSerializer, VenueDetailSerializer, RatingSerializer
from suburbs.models import Suburb

class VenueList(APIView):
    # Handles the list of all venues.
    # GET /api/venues/ Returns a list of all venues (excluding archived ones)
    # POST /api/venues/ Creates a new venue

    
    def get(self, request):
        # Get all venues that haven't been archived.
        venues = Venue.objects.filter(is_archived=False)

        # KEY FOR FRONTEND
        
        # Filter by main category (set by which tab the user clicked)
        main_category = request.GET.get('main_category', '')
        if main_category:
            venues = venues.filter(main_category=main_category)

        # Filter by suburb (set by the autocomplete in "where")
        suburb = request.GET.get('suburb', '')
        if suburb:
            venues = venues.filter(suburb__iexact=suburb)

        # Filter by indoor/outdoor (the "What?" buttons)
        indoor_outdoor = request.GET.get('indoor_outdoor', '')
        if indoor_outdoor:
            venues = venues.filter(indoor_outdoor__iexact=indoor_outdoor)

         # Filter by age (the "Who" field — kid's age)
        age = request.GET.get('age', '')
        if age:
        # min_age <= age <= max_age
            venues = venues.filter(min_age__lte=age, max_age__gte=age)
        
        # If a suburb was searched but no venues came back, work out WHY so the frontend can show a friendly message instead of an empty list.
        # This block returns a special response shape with a status field, only on the "no venues found" cases.
        # The successful path below still returns a flat array, so existing frontend code keeps working.
        if suburb and not venues.exists():
            # Try NSW first - the autocomplete only shows NSW suburbs, an NSW match is what the user almost certainly meant.
            # This matters for suburb names that exist in multiple states (e.g. Newtown is in NSW, VIC, and QLD).
            suburb_record = Suburb.objects.filter(
                suburb__iexact=suburb,
                state='NSW'
            ).first()

            # If no NSW match, fall back to any state — this catches users who somehow searched for a non-NSW suburb (e.g. typed it in the URL).
            if not suburb_record:
                suburb_record = Suburb.objects.filter(suburb__iexact=suburb).first()

            if not suburb_record:
                # The suburb name isn't in our Suburb table at all (typo or made-up name like "Hogsmeade")
                return Response({
                    'status': 'unknown_suburb',
                    'suburb': suburb,
                    'venues': [],
                })

            if suburb_record.state != 'NSW':
                # Suburb exists but isn't in NSW (e.g. Melbourne in VIC), frontend will show: "We're only built for NSW..."
                return Response({
                    'status': 'unsupported_state',
                    'suburb': suburb_record.suburb,
                    'state': suburb_record.state,
                    'venues': [],
                })

            # Suburb is in NSW but no venues match the current filters., frontend will show: "Nothing logged in {suburb} yet..."
            return Response({
                'status': 'no_venues_in_nsw_suburb',
                'suburb': suburb_record.suburb,
                'state': 'NSW',
                'venues': [],
            })

        # Normal case — venues found (or no suburb filter at all).
        # Serializer turns the venue objects into JSON the frontend can use.
        # Returns a flat array, unchanged from the original behaviour.
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
        venue = get_object_or_404(Venue, pk=pk, is_archived=False)
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

    def delete(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk, is_archived=False)
        venue.is_archived = True
        venue.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RatingList(APIView):
    # GET /api/venues/<venue_pk>/ratings/ — list all ratings for a venue
    # POST /api/venues/<venue_pk>/ratings/ — create a rating for a venue

    def get(self, request, venue_pk):
        venue = get_object_or_404(Venue, pk=venue_pk)
        ratings = Rating.objects.filter(venue=venue, is_archived=False)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    def post(self, request, venue_pk):
        venue = get_object_or_404(Venue, pk=venue_pk)
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, venue=venue)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingDetail(APIView):
    # GET /api/venues/<venue_pk>/ratings/<pk>/ — get a single rating

    def get(self, request, venue_pk, pk):
        rating = get_object_or_404(Rating, pk=pk, venue=venue_pk, is_archived=False)
        serializer = RatingSerializer(rating)
        return Response(serializer.data)