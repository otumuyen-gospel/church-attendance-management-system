from rest_framework import serializers
from .models import Faces

class FacesSerializers(serializers.ModelSerializer):

    class Meta:
        model = Faces
        # Exclude binary field to prevent UTF-8 decoding errors
        exclude = ['faceEncoding']