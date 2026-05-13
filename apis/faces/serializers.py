from rest_framework import serializers
from .models import Faces
from .apps import FacesConfig

storage = FacesConfig.storage

class FacesSerializers(serializers.ModelSerializer):
    pics = serializers.SerializerMethodField()
    class Meta:
        model = Faces
        fields = ['id', 'pics', 'personId', ]

    def get_pics(self, obj):
        if obj.pics:
            return storage.get_url(str(obj.pics))
        return None

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