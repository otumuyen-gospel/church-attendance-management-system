from rest_framework import serializers
from .models import Membership

class MembershipSerializers(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = "__all__"