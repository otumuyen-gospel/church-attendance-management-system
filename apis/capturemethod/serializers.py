from rest_framework import serializers
from .models import CaptureMethod

class CaptureMethodSerializers(serializers.ModelSerializer):
    class Meta:
        model = CaptureMethod
        fields = '__all__'
