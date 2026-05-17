from rest_framework import serializers
from .models import Followup
from django.utils import timezone

class FollowupSerializers(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    creatorId = serializers.SerializerMethodField()
    class Meta:
        model = Followup
        fields = "__all__"

    def get_status(self, obj):
        # If it is past the due date and not already completed, return OVERDUE
        if obj.status != 'COMPLETED' and obj.dueDate < timezone.localdate():
            return 'OVERDUE'
        return obj.status

    def get_creatorId(self, obj):
        return obj.creatorId.id if obj.creatorId else None