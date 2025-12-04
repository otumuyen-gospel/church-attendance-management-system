from rest_framework import serializers
from .models import Faces

class FacesSerializers(serializers.ModelSerializer):

    class Meta:
        model = Faces
        fields = "__all__"