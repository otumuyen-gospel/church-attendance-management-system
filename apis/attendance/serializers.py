from rest_framework import serializers
from .models import Attendance

class attendanceSerializers(serializers.ModelSerializer):

    class Meta:
        models = Attendance
        fields = "__all__"