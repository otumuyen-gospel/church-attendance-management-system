"""
Unit tests for face recognition system
Run with: python manage.py test faces
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io
import numpy as np
from person.models import Person
from .models import Faces
from .views import FaceRecognitionEngine, FaceEncodingCache
from .tasks import generate_face_encoding_async
import logging

logger = logging.getLogger(__name__)


class FaceRecognitionEngineTests(TestCase):
    """Test FaceRecognitionEngine methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a simple test image
        self.test_image = self._create_test_image()
        
    def _create_test_image(self, size=(200, 200)):
        """Create a simple test image"""
        img = Image.new('RGB', size, color='red')
        return np.array(img)
    
    def test_process_image_stream_with_bytes(self):
        """Test image stream processing with bytes input"""
        # Create image bytes
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Process
        result, success = FaceRecognitionEngine.process_image_stream(img_bytes.getvalue())
        
        self.assertTrue(success)
        self.assertEqual(result.shape, (100, 100, 3))
    
    def test_process_image_stream_with_file(self):
        """Test image stream processing with file object"""
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        result, success = FaceRecognitionEngine.process_image_stream(img_bytes)
        
        self.assertTrue(success)
        self.assertIsNotNone(result)
    
    def test_compare_faces_empty_dict(self):
        """Test face comparison with empty encoding dictionary"""
        test_encoding = np.random.rand(128)
        matches = FaceRecognitionEngine.compare_faces_efficient(
            test_encoding,
            {}
        )
        
        self.assertEqual(matches, [])
    
    def test_compare_faces_with_data(self):
        """Test face comparison with known encodings"""
        test_encoding = np.random.rand(128)
        known_encodings = {
            1: {
                'encoding': np.random.rand(128),
                'person_id': 1,
                'person_name': 'Test Person',
                'face_id': 1
            }
        }
        
        matches = FaceRecognitionEngine.compare_faces_efficient(
            test_encoding,
            known_encodings
        )
        
        self.assertEqual(len(matches), 1)
        self.assertIn('distance', matches[0])
        self.assertIn('is_match', matches[0])
        self.assertIn('confidence', matches[0])


class FaceEncodingCacheTests(TestCase):
    """Test FaceEncodingCache functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear cache before each test
        FaceEncodingCache.clear_cache()
    
    def tearDown(self):
        """Clean up after tests"""
        FaceEncodingCache.clear_cache()
    
    def test_load_all_encodings_empty(self):
        """Test loading encodings when none exist"""
        encodings = FaceEncodingCache.load_all_encodings()
        self.assertEqual(encodings, {})
    
    def test_clear_cache(self):
        """Test cache clearing"""
        # Load encodings (creates cache)
        FaceEncodingCache.load_all_encodings()
        
        # Clear cache
        FaceEncodingCache.clear_cache()
        
        # Verify cache is cleared
        from django.core.cache import cache
        self.assertIsNone(cache.get(FaceEncodingCache.CACHE_KEY))


class FaceRecognitionAPITests(APITestCase):
    """Test face recognition API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test person
        self.person = Person.objects.create(
            firstName='Test',
            lastName='Person'
        )
        
        # Clear cache
        FaceEncodingCache.clear_cache()
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def _create_test_image_file(self, name='test.jpg'):
        """Create a test image file"""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        img_bytes.name = name
        return img_bytes
    
    def test_recognize_no_image_provided(self):
        """Test recognition without image"""
        response = self.client.post('/api/faces/recognize/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Image file is required', response.data['error'])
    
    def test_recognize_with_image_no_face(self):
        """Test recognition with image that has no face"""
        image = self._create_test_image_file()
        response = self.client.post(
            '/api/faces/recognize/',
            {'image': image},
            format='multipart'
        )
        
        # Should return 400 since no face detected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('No face detected', response.data['error'])
    
    def test_batch_recognize_no_images(self):
        """Test batch recognition without images"""
        response = self.client.post('/api/faces/batch-recognize/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('No images provided', response.data['error'])
    
    def test_cache_management_reload(self):
        """Test cache reload endpoint"""
        response = self.client.post(
            '/api/faces/cache/',
            {'action': 'reload'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('encodings_loaded', response.data)
    
    def test_cache_management_clear(self):
        """Test cache clear endpoint"""
        response = self.client.post(
            '/api/faces/cache/',
            {'action': 'clear'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('cleared', response.data['message'])
    
    def test_cache_management_invalid_action(self):
        """Test cache with invalid action"""
        response = self.client.post(
            '/api/faces/cache/',
            {'action': 'invalid'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class BackgroundTaskTests(TestCase):
    """Test background task functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.person = Person.objects.create(
            firstName='Test',
            lastName='Person'
        )
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='blue')
        img_path = '/tmp/test_image.jpg'
        img.save(img_path)
        
        # Create face
        self.face = Faces.objects.create(
            personId=self.person,
            pics='/path/to/test.jpg'  # Non-existent for testing
        )
    
    def test_generate_face_encoding_invalid_id(self):
        """Test encoding generation with invalid face ID"""
        result = generate_face_encoding_async(99999)
        self.assertFalse(result)
    
    def test_generate_face_encoding_no_images(self):
        """Test encoding generation when images don't exist"""
        result = generate_face_encoding_async(self.face.id)
        # Should handle gracefully
        self.assertFalse(result)


class ImageProcessingTests(TestCase):
    """Test image processing utilities"""
    
    def test_process_different_image_formats(self):
        """Test processing of different image formats"""
        formats = ['JPEG', 'PNG', 'BMP']
        
        for fmt in formats:
            img = Image.new('RGB', (100, 100), color='green')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=fmt)
            img_bytes.seek(0)
            
            result, success = FaceRecognitionEngine.process_image_stream(img_bytes.getvalue())
            
            self.assertTrue(success)
            self.assertEqual(result.shape, (100, 100, 3))
    
    def test_process_image_with_invalid_data(self):
        """Test processing with invalid image data"""
        invalid_data = b'not an image'
        result, success = FaceRecognitionEngine.process_image_stream(invalid_data)
        
        self.assertFalse(success)
        self.assertIsNone(result)


class PerformanceTests(TestCase):
    """Test performance characteristics"""
    
    def test_comparison_performance_with_many_encodings(self):
        """Test comparison speed with many known encodings"""
        import time
        
        # Create many test encodings
        known_encodings = {}
        for i in range(1000):
            known_encodings[i] = {
                'encoding': np.random.rand(128),
                'person_id': i,
                'person_name': f'Person {i}',
                'face_id': i
            }
        
        test_encoding = np.random.rand(128)
        
        # Time the comparison
        start = time.time()
        matches = FaceRecognitionEngine.compare_faces_efficient(
            test_encoding,
            known_encodings
        )
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        self.assertLess(elapsed, 1.0)  # Less than 1 second for 1000 comparisons
        self.assertEqual(len(matches), 1000)
