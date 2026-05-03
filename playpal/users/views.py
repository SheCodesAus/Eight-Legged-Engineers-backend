## pulling dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from .models import CustomUsers, Kids
from .serializers import CustomUserSerializer, KidsSerializer, CustomUserDetailSerializer
from .permissions import IsUserOrReadOnly, IsKidOwnerOrReadOnly


class CustomUsersList(APIView):

    permission_classes = [
        IsUserOrReadOnly,
    ]

    ## Get all users with their kids
    def get(self, request):
        customusers = CustomUsers.objects.all()
        serializer = CustomUserDetailSerializer(customusers, many=True)
        return Response(serializer.data)
    
    ## Create user
    def post(self, request):
        ## to serialise as json
        serializer = CustomUserSerializer(data=request.data) 
        ## built in function is_valid - valid as json format
        if serializer.is_valid(): 
            ## call another function to save the data
            serializer.save() 
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        ## if response is invalid, return error 400
        return Response( 
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

class CustomUsersDetailsList(APIView):

    permission_classes = [
        IsUserOrReadOnly,
    ]

    ## Get an user
    def get(self, request, pk):
        ## show one user. helper function get_object_or_404
        customuser = get_object_or_404(CustomUsers, pk=pk)
        ## Add the nested serializer
        serializer = CustomUserDetailSerializer(customuser) 
        return Response(serializer.data)


class KidsList(APIView):

    permission_classes = [
        IsKidOwnerOrReadOnly,
    ]

    ## Create kid
    def post(self, request):
        ## to serialise as json
        serializer = KidsSerializer(data=request.data) 
        ## built in function is_valid - valid as json format
        if serializer.is_valid(): 
            ## call another function to save the data
            serializer.save(user_id=request.user) 
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        ## if response is invalid, return error 400
        return Response( 
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class KidsDetail(APIView):

    permission_classes = [
        IsKidOwnerOrReadOnly,
    ]
    ## Get a kid
    def get(self, request, pk):
        kids = get_object_or_404(Kids, pk=pk) 
        serializer = KidsSerializer(kids) 
        return Response(serializer.data)