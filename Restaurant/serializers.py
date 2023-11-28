from rest_framework import serializers
from .models import Waiter

class WaiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waiter
        fields = ['name', 'email', 'address', ]

from rest_framework import serializers
from .models import Cook

class CookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cook
        fields = ['name', 'email', ]

