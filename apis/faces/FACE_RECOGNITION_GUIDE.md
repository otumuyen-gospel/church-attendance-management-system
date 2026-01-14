# Face Recognition System Documentation

## Overview

This system provides real-time face recognition with streaming image support, efficient face encoding storage, and background processing capabilities. It uses:

- **face_recognition**: For face detection and encoding generation
- **numpy**: For efficient vectorized distance calculations
- **pickle**: For serializing face encodings
- **Django Cache**: For efficient encoding caching
- **ThreadPoolExecutor**: For parallel batch processing
- **Celery** (optional): For distributed async task processing

## Features

### 1. Real-time Face Recognition
- **Endpoint**: `POST /api/faces/recognize/`
- **Purpose**: Stream image and get immediate face recognition results
- **Performance**: ~200-500ms per image (GPU accelerated if available)

### 2. Batch Face Recognition
- **Endpoint**: `POST /api/faces/batch-recognize/`
- **Purpose**: Process multiple images in parallel
- **Performance**: Scales with available CPU cores

### 3. Cache Management
- **Endpoint**: `POST /api/faces/cache/`
- **Purpose**: Clear or reload face encoding cache
- **Benefit**: Faster recognition after adding new faces

### 4. Background Task Processing
- Face encoding generation from uploaded images
- Batch encoding regeneration
- Optional Celery integration for distributed processing

## API Endpoints

### 1. Face Recognition Stream

```
POST /api/faces/recognize/
Content-Type: multipart/form-data

Body:
- image: Image file (required)
- return_all_matches: boolean (optional, default: false)
- match_count: integer (optional, default: 5)

Response:
{
    "success": true,
    "message": "Face recognition completed",
    "top_match": {
        "face_id": 1,
        "person_id": 123,
        "person_name": "John Doe",
        "distance": 0.45,
        "is_match": true,
        "confidence": 0.85
    },
    "top_matches": [...],
    "total_matches_found": 3,
    "processing_time_ms": 245.32
}
```

**Usage Example** (Python):
```python
import requests

url = "http://localhost:8000/api/faces/recognize/"
with open("image.jpg", "rb") as img:
    files = {"image": img}
    response = requests.post(url, files=files, headers={
        "Authorization": "Bearer YOUR_TOKEN"
    })
    print(response.json())
```

**Usage Example** (cURL):
```bash
curl -X POST http://localhost:8000/api/faces/recognize/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@image.jpg"
```

### 2. Batch Face Recognition

```
POST /api/faces/batch-recognize/
Content-Type: multipart/form-data

Body:
- images: Multiple image files (required)

Response:
{
    "success": true,
    "total_images": 5,
    "processed": 5,
    "failed": 0,
    "results": [
        {
            "success": true,
            "index": 0,
            "filename": "person1.jpg",
            "top_match": {...},
            "matches_found": 2
        },
        ...
    ],
    "processing_time_ms": 1243.45
}
```

### 3. Cache Management

```
POST /api/faces/cache/
Content-Type: application/json

Body:
{
    "action": "reload"  // or "clear"
}

Response:
{
    "success": true,
    "message": "Face encoding cache reloaded",
    "encodings_loaded": 150
}
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key libraries added:
- `face-recognition==1.3.5` - Face detection and encoding
- `numpy==2.3.5` - Vectorized operations (already installed)
- `pillow==12.0.0` - Image processing (already installed)

### 2. Configure Django Settings

Add to `apis/settings.py`:

```python
# Cache configuration for face encodings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'face-encoding-cache',
        'TIMEOUT': 3600,  # 1 hour
    }
}

# Logging for face recognition
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'faces': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. (Optional) Configure Celery

For production async processing:

```bash
pip install celery[redis]
```

Update `apis/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'celery',
    ...
]

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

Create `apis/celery.py`:

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apis.settings')

app = Celery('apis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

Update `apis/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

Run Celery worker:

```bash
celery -A apis worker -l info
```

## Usage Patterns

### Pattern 1: Direct Face Recognition (Synchronous)

```python
from rest_framework.test import APIClient

client = APIClient()
client.credentials(HTTP_AUTHORIZATION='Bearer YOUR_TOKEN')

with open("test_image.jpg", "rb") as img:
    response = client.post('/api/faces/recognize/', 
                          {'image': img}, 
                          format='multipart')
    
    data = response.json()
    if data['success']:
        top_match = data['top_match']
        if top_match:
            print(f"Match: {top_match['person_name']}")
            print(f"Confidence: {top_match['confidence']:.2%}")
```

### Pattern 2: Batch Processing

```python
import glob

images = glob.glob("attendance_photos/*.jpg")
image_files = [open(img, 'rb') for img in images]

response = client.post('/api/faces/batch-recognize/', 
                      {'images': image_files}, 
                      format='multipart')

for result in response.json()['results']:
    if result['success'] and result['top_match']:
        print(f"{result['filename']}: {result['top_match']['person_name']}")
```

### Pattern 3: Background Encoding Generation

```python
from faces.tasks import generate_face_encoding_async

# Synchronous
result = generate_face_encoding_async(face_id=123)

# With Celery (async)
from faces.celery_tasks import celery_generate_face_encoding
celery_generate_face_encoding.delay(face_id=123)
```

### Pattern 4: Cache Management

```python
# Clear cache after adding new faces
response = client.post('/api/faces/cache/', 
                      {'action': 'clear'})

# Reload from database
response = client.post('/api/faces/cache/', 
                      {'action': 'reload'})
```

## Performance Optimization

### 1. Encoding Caching
- All encodings loaded at startup and cached in memory
- Cache timeout: 1 hour (configurable)
- Auto-cleared when new faces added

### 2. Vectorized Operations
```python
# Efficient numpy distance computation
distances = np.linalg.norm(test_encoding - known_encodings, axis=1)
```

### 3. Face Detection Models
```python
# HOG model: Fast, CPU-friendly
# CNN model: Accurate but GPU-required
face_recognition.face_locations(image, model='hog')  # Default
face_recognition.face_locations(image, model='cnn')  # GPU
```

### 4. ThreadPool for Batch Processing
- Uses 4 worker threads by default
- Processes images in parallel
- Configurable via `max_workers` parameter

### 5. Database Query Optimization
```python
# Only load faces with encodings
faces = Faces.objects.filter(faceEncoding__isnull=False)
```

## Configuration Parameters

### FaceRecognitionEngine

```python
class FaceRecognitionEngine:
    DISTANCE_THRESHOLD = 0.6  # Lower = stricter matching
```

**Threshold Guidelines:**
- 0.5: Very strict (high accuracy, may miss some matches)
- 0.6: Balanced (recommended)
- 0.7: Lenient (may have false positives)

### FaceEncodingCache

```python
class FaceEncodingCache:
    CACHE_TIMEOUT = 3600  # 1 hour in seconds
    CACHE_KEY = "face_encodings_cache"
```

### ThreadPoolExecutor

```python
# In BatchFaceRecognitionView._process_single_image
with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust as needed
```

**Worker Guidelines:**
- 2-4: Small deployments
- 4-8: Medium deployments
- 8+: Large deployments with dedicated hardware

## Error Handling

### Common Errors

```python
# No face detected
Response: {"success": False, "error": "No face detected in image"}

# Image processing failed
Response: {"success": False, "error": "Failed to process image"}

# No faces in database
Response: {"success": False, "error": "No face data available in database"}

# Server error
Response: {"success": False, "error": "Face recognition error: ..."}
```

### Logging

Check Django logs for detailed error information:

```python
import logging
logger = logging.getLogger('faces')
```

## Security Considerations

1. **Permission Classes**: All endpoints require `IsAuthenticated`
2. **Group Permissions**: 
   - Recognition: `view_faces` permission
   - Cache Management: `IsAdminUser` only
3. **File Upload Limits**: Configure in Django settings
4. **CSRF Protection**: Django middleware handles

```python
# Add to settings.py for file size limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600
```

## Monitoring & Diagnostics

### Check Cache Status

```python
from django.core.cache import cache
from faces.views import FaceEncodingCache

# Get cached encodings count
encodings = FaceEncodingCache.load_all_encodings()
print(f"Cached encodings: {len(encodings)}")

# Clear if needed
FaceEncodingCache.clear_cache()
```

### Performance Metrics

The API returns `processing_time_ms` for each request:

```python
# Single recognition: 200-500ms
# Batch (10 images): 2-5 seconds
# With GPU: 50-200ms per image
```

### Database Queries

Monitor queries with Django Debug Toolbar:

```python
# settings.py
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
```

## Advanced Usage

### Custom Distance Thresholds

```python
# Modify in FaceRecognitionEngine
FaceRecognitionEngine.DISTANCE_THRESHOLD = 0.5  # Stricter
```

### GPU Acceleration

For faster face detection:

```python
# faces/views.py
def generate_face_encoding(image_array):
    face_locations = face_recognition.face_locations(image_array, model='cnn')
    # CNN model requires CUDA-capable GPU
```

### Bulk Encoding Generation

```python
from faces.tasks import batch_generate_encodings_async

# Generate for all faces without encoding
result = batch_generate_encodings_async()
print(f"Success: {result['success']}, Failed: {result['failed']}")
```

## Troubleshooting

### Problem: "No face detected"

**Solutions:**
- Image quality too low
- Face too small in image
- Poor lighting
- Face partially obscured

### Problem: High False Positives

**Solutions:**
- Lower `DISTANCE_THRESHOLD` (more strict)
- Increase encoding data (add more images per person)
- Use better quality images

### Problem: Slow Performance

**Solutions:**
- Clear and reload cache
- Increase `max_workers` for batch processing
- Use GPU acceleration for detection
- Optimize image sizes before upload

## Contributing

To add new features:

1. Add new methods to `FaceRecognitionEngine`
2. Create views that use the engine
3. Add appropriate unit tests
4. Update this documentation

## References

- [face_recognition Documentation](https://github.com/ageitgey/face_recognition)
- [dlib Documentation](http://dlib.net/python/index.html)
- [Django Cache Framework](https://docs.djangoproject.com/en/4.2/topics/cache/)
- [Celery Tasks](https://docs.celeryproject.org/)
