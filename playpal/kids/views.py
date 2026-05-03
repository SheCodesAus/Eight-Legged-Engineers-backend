from rest_framework import viewsets
from .models import Kid
from .serializers import KidSerializer


class KidView(viewsets.ModelViewSet):
    queryset = Kid.objects.all()
    serializer_class = KidSerializer
