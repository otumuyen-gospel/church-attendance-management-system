from rest_framework import serializers
from .models import Attendance

class attendanceSerializers(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"


class RecognizeFormSerializer(serializers.Serializer):
    fullname = serializers.CharField(required=True)
    servicesId = serializers.IntegerField(required=True)