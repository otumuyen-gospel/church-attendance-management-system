from rest_framework import serializers
from .models import Attendance

class attendanceSerializers(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"