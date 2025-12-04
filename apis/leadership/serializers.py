from rest_framework import serializers
from .models import Leadership


class LeadershipSerializers(serializers.ModelSerializer):

    class Meta:
        model = Leadership
        fields = "__all__"