from rest_framework import serializers
from .models import Myapp

class MyappSerializers(serializers.ModelSerializer):
    class Meta:
        model = Myapp
        fields = '__all__'