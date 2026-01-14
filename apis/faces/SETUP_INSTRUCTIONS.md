"""
SETUP_INSTRUCTIONS.md - Complete setup guide for Face Recognition System
"""

# Complete Setup Instructions for Face Recognition System

## Step 1: Install Dependencies

```bash
# Navigate to the apis directory
cd apis

# Install face_recognition and other dependencies
pip install -r requirements.txt

# If you encounter issues with face_recognition on Windows:
pip install face-recognition --only-binary=:all:
```

## Step 2: Update Django Settings

Add the following to `apis/settings.py`:

```python
# ============================================================================
# FACE RECOGNITION CONFIGURATION
# ============================================================================

# Cache configuration for face encodings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 3600,  # 1 hour - adjust as needed
        'OPTIONS': {
            'MAX_ENTRIES': 10000  # Allow many encodings
        }
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/face_recognition.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'faces': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# File upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600   # 100MB
FILE_UPLOAD_TEMP_DIR = 'temp_uploads/'

# Optional: Face Recognition Settings
FACE_RECOGNITION = {
    'DISTANCE_THRESHOLD': 0.6,  # 0.5=strict, 0.6=balanced, 0.7=lenient
    'DETECTION_MODEL': 'hog',    # 'hog' (fast) or 'cnn' (accurate, needs GPU)
    'CACHE_TIMEOUT': 3600,       # seconds
    'BATCH_WORKERS': 4,           # Number of parallel workers
}
```

## Step 3: Create Logs Directory

```bash
# In the apis root directory
mkdir -p logs
touch logs/face_recognition.log
```

## Step 4: Run Migrations

```bash
python manage.py migrate
```

## Step 5: Test Installation

```bash
# Run face recognition tests
python manage.py test faces

# Expected output:
# Ran XX tests in X.XXXs
# OK
```

## Step 6 (Optional): Set Up Celery for Production

If you want async background processing for large-scale deployments:

### 6a. Install Celery and Redis

```bash
pip install celery[redis]==5.3.0
pip install redis==5.0.0
```

### 6b. Update settings.py

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'celery',
    ...
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
```

### 6c. Update apis/__init__.py

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 6d. Create apis/celery.py

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apis.settings')

app = Celery('apis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

### 6e. Start Celery Worker

```bash
# In a separate terminal
celery -A apis worker -l info

# With concurrency (process pool)
celery -A apis worker -l info --concurrency=4
```

## Step 7: Load Initial Face Data

```bash
# In Django shell
python manage.py shell
```

```python
from faces.tasks import batch_generate_encodings_async
from faces.views import FaceEncodingCache

# Generate encodings for all faces without them
result = batch_generate_encodings_async()
print(f"Generated {result['success']} encodings, {result['failed']} failed")

# Load encodings into cache
encodings = FaceEncodingCache.load_all_encodings()
print(f"Loaded {len(encodings)} encodings into cache")
```

## Step 8: Test API Endpoints

### Using cURL

```bash
# Test face recognition
curl -X POST http://localhost:8000/api/faces/recognize/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@test_image.jpg"

# Test cache management
curl -X POST http://localhost:8000/api/faces/cache/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "reload"}'
```

### Using Python

```python
import requests
from PIL import Image
import io

# Create test image
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Send request
response = requests.post(
    'http://localhost:8000/api/faces/recognize/',
    files={'image': img_bytes},
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

print(response.json())
```

## Step 9: Configure Admin Panel

Access Django admin at `/admin/`:

1. Go to Faces section
2. Select faces and choose "Generate face encoding for selected faces"
3. Check "Encoding Information" for generation status

## Step 10: Monitor Performance

```python
# In Django shell
from faces.views import FaceEncodingCache
from django.core.cache import cache

# Check cache status
encodings = FaceEncodingCache.load_all_encodings()
print(f"Cached encodings: {len(encodings)}")

# Check cache backend
cache_info = cache.get_stats() if hasattr(cache, 'get_stats') else "N/A"
print(f"Cache stats: {cache_info}")
```

## Troubleshooting

### Issue: "No module named face_recognition"

**Solution:**
```bash
# On Windows, use binary wheels
pip install --only-binary=:all: face-recognition

# On Mac/Linux
brew install dlib  # macOS
sudo apt-get install libdlib-dev  # Ubuntu/Debian
pip install face-recognition
```

### Issue: "dlib" build errors

**Windows:**
```bash
# Install visual C++ build tools or use pre-built wheels
pip install face-recognition --only-binary=:all:
```

**macOS:**
```bash
# Install Xcode command line tools
xcode-select --install
pip install face-recognition
```

### Issue: Low recognition accuracy

**Solutions:**
1. Increase `DISTANCE_THRESHOLD` (more lenient matching)
2. Add more images per person to encode
3. Use higher quality images (min 100x100 pixels)
4. Use 'cnn' detection model for accuracy (requires GPU)

### Issue: Slow performance

**Solutions:**
1. Clear cache: `/api/faces/cache/` with action='clear'
2. Increase `BATCH_WORKERS` for batch processing
3. Use GPU acceleration: change `DETECTION_MODEL` to 'cnn'
4. Optimize batch size in requests

## Performance Benchmarks

### Single Face Recognition
- Without GPU: 200-500ms per image
- With GPU (CUDA): 50-200ms per image

### Batch Recognition (10 images)
- Without GPU: 2-5 seconds
- With GPU: 0.5-2 seconds

### Cache Load
- First time: 100-500ms (depends on face count)
- Subsequent: <1ms (in-memory)

## Security Checklist

- [ ] Enable HTTPS in production
- [ ] Set appropriate file upload limits
- [ ] Configure CORS properly
- [ ] Use strong API tokens
- [ ] Enable logging for audit trails
- [ ] Regular backup of face encodings
- [ ] Limit API rate if needed

## Production Deployment Checklist

- [ ] Use PostgreSQL or MySQL (not SQLite)
- [ ] Configure Redis for caching
- [ ] Set up Celery workers for async tasks
- [ ] Enable HTTPS and CORS
- [ ] Configure log rotation
- [ ] Set up monitoring/alerts
- [ ] Regular backup strategy
- [ ] Load testing for your use case

## Next Steps

1. Read [FACE_RECOGNITION_GUIDE.md](./FACE_RECOGNITION_GUIDE.md) for detailed API documentation
2. Configure API authentication according to your needs
3. Set up monitoring for recognition accuracy
4. Train on your specific use case for better results
5. Consider GPU setup for high-performance requirements

## Support Resources

- [face_recognition GitHub](https://github.com/ageitgey/face_recognition)
- [Django Cache Framework](https://docs.djangoproject.com/en/4.2/topics/cache/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [DRF Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
