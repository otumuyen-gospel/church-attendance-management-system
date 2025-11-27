from rest_framework import serializers
from .models import HouseHold

class HouseHoldSerializers(serializers.ModelSerializer):
    class Meta:
        model = HouseHold
        fields = '__all__'
