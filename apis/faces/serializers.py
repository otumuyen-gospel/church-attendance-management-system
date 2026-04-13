from rest_framework import serializers
from .models import Faces

class FacesSerializers(serializers.ModelSerializer):

    class Meta:
        model = Faces
        fields = ['id', 'pics', 'personId', ]


class RecognizeFaceSerializer(serializers.Serializer):
    pics = serializers.FileField(required=True)
    servicesId = serializers.IntegerField(required=True)

class CreateFaceSerializer(serializers.Serializer):
    frontview = serializers.FileField(required=True)
    leftsideview = serializers.FileField(required=True)
    rightsideview = serializers.FileField(required=True)
    smileview = serializers.FileField(required=True)
    frownview = serializers.FileField(required=True)
    personId = serializers.IntegerField(required=True)