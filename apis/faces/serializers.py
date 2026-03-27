from rest_framework import serializers
from .models import Faces

class FacesSerializers(serializers.ModelSerializer):
    encoding = serializers.JSONField(allow_null=True, required=False)

    class Meta:
        model = Faces
        fields = '__all__'


class RecognizeFaceSerializer(serializers.Serializer):
    pics = serializers.FileField(required=True)
