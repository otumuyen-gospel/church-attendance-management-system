from rest_framework import serializers
from .models import Church
from supabase import create_client, Client
from django.conf import settings


# Initialize Supabase client only if not in DEBUG mode
supabase = None
if not settings.DEBUG:
    supabase: Client = create_client(settings.SUPERBASE_URL, settings.SERVICE_ROLE_KEY)

class ChurchSerializers(serializers.ModelSerializer):

    logo = serializers.SerializerMethodField()

    class Meta:
        model = Church
        fields = ['id', 'logo', 'address', 'description', 'name']
    
    def get_logo(self, obj):
        if not obj.logo:
            return None

        # --- DEVELOPMENT ENVIRONMENT ---
        if settings.DEBUG:
            # Returns the local URL (e.g., /media/logos/image.png)
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url

        # --- PRODUCTION ENVIRONMENT ---
        try:
            file_path = obj.logo.name
            # Note: Ensure bucket name is consistent with your prod setup
            response = supabase.storage.from_(settings.AWS_STORAGE_BUCKET_NAME).create_signed_url(
                path=file_path, 
                expires_in=3600
            )
            return response.get('signedURL')
        except Exception:
            # Fallback to standard URL if Supabase call fails
            return obj.logo.url if hasattr(obj.logo, 'url') else str(obj.logo)
