import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from supabase import create_client

class StorageService:
    def __init__(self):
        # Detect environment
        self.local = os.environ.get("APP_ENV", "local") == "local"
        
        if not self.local:
            #hybrid and production mode
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            self.client = create_client(settings.SUPERBASE_URL, settings.SERVICE_ROLE_KEY)
        else:
            # Ensure local media directory exists
            self._ensure_local_dir("uploads")

    def _ensure_local_dir(self, folder):
        """Creates the local directory if it doesn't exist"""
        path = os.path.join(settings.MEDIA_ROOT, folder)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    def _generate_unique_name(self, filename):
        ext = filename.split('.')[-1]
        return f"{uuid.uuid4()}.{ext}"

    def upload_file(self, file_obj, folder="uploads"):
        unique_name = self._generate_unique_name(file_obj.name)
        path = f"{folder}/{unique_name}"

        if not self.local:
            # Upload to Supabase
            self.client.storage.from_(self.bucket_name).upload(
                path=path,
                file=file_obj.read(),
                file_options={"content-type": file_obj.content_type}
            )
        else:
            # Save to local disk (/media/uploads/...)
            # We use default_storage which respects MEDIA_ROOT
            path = default_storage.save(path, file_obj)
        
        return path

    def update_file(self, old_path, new_file_obj, folder="uploads"):
        if old_path:
            self.delete_file(old_path)
        return self.upload_file(new_file_obj, folder)

    def delete_file(self, path):
        if not path: return
        
        if not self.local:
            self.client.storage.from_(self.bucket_name).remove([path])
        else:
            if default_storage.exists(path):
                default_storage.delete(path)

    def get_url(self, path, expires_in=86400): #expires in 24hrs makes the engine more faster
        if not path: return None

        if not self.local:
            try:
                res = self.client.storage.from_(self.bucket_name).create_signed_url(path, expires_in)
                return res.get('signedURL')
            except Exception:
                return None
        else:
            # Return local URL: e.g., http://127.0.0
            return f"{settings.SITE_URL}/{path}"
        
