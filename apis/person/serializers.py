from rest_framework import serializers
from .models import Person

class PersonSerializers(serializers.ModelSerializer):
    age = serializers.ReadOnlyField() 
    class Meta:
        model = Person
        fields = "__all__"