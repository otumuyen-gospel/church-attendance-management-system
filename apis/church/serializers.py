from rest_framework import serializers
from .models import Church
from supabase import create_client, Client
from django.conf import settings

from faces.apps import FacesConfig

storage = FacesConfig.storage

class ChurchSerializers(serializers.ModelSerializer):

    logo = serializers.SerializerMethodField()

    class Meta:
        model = Church
        fields = ['id', 'logo', 'address', 'description', 'name']
    
    def get_logo(self, obj):
        if obj.logo:
            return storage.get_url(str(obj.logo))
        return None