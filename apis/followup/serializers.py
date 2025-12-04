from rest_framework import serializers
from .models import FollowUp


class FollowUpSerializers(serializers.ModelSerializer):

    class Meta:
        model = FollowUp
        fields = "__all__"