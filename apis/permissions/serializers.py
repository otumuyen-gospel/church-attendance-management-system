from rest_framework import serializers
from .models import Permissions

class PermissionsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Permissions
        fields = "__all__"