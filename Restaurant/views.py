from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Waiter
from .serializers import WaiterSerializer

class WaiterViewSet(viewsets.ModelViewSet):
    queryset = Waiter.objects.all()
    serializer_class = WaiterSerializer

from .models import Cook
from .serializers import CookSerializer

class CookViewSet(viewsets.ModelViewSet):
    queryset = Cook.objects.all()
    serializer_class = CookSerializer

