from urllib import request
from django.shortcuts import render

# Create your views here.
from .models import Faces
from .serializers import FacesSerializers
from django.shortcuts import render
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from urllib.parse import urlparse
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from django_filters import AllValuesFilter, DateTimeFilter, NumberFilter
from rest_framework.exceptions import PermissionDenied
from django.http import HttpResponse, FileResponse
from rest_framework.views import APIView
from role.util import requiredGroups
from user.permissions import IsInGroup
import numpy as np
from PIL import Image
import io
import hashlib
import pickle
from .tasks import generate_face_encoding_async 
from attendance.models import Attendance
from capturemethod.models import CaptureMethod
from person.models import Person
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor
import logging
import os

logger = logging.getLogger(__name__)


class FaceFrontendView(APIView):
    """
    Serve the face recognition frontend HTML
    Accessible at /user_faces/frontend/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return the face recognition HTML frontend"""
        try:
            # Get the path to the HTML file
            html_file_path = os.path.join(
                os.path.dirname(__file__), 
                'face_frontend.html'
            )
            
            if os.path.exists(html_file_path):
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return HttpResponse(html_content, content_type='text/html')
            else:
                return Response(
                    {
                        'error': 'Frontend HTML file not found',
                        'path': html_file_path
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            logger.error(f"Error serving frontend: {str(e)}")
            return Response(
                {'error': f'Failed to load frontend: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


#this generic class will handle GET method to be used by the admin alone
class FacesList(generics.ListAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [AllowAny]
   # required_groups = requiredGroups(permission='view_faces')
    name = 'faces-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('personId__id',) 

     #you can search using the "search" keyword
    search_fields = ('personId__id')

    #you can order using the "ordering" keyword
    ordering_fields = ('personId__id',)


class UpdateFaces(generics.UpdateAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='change_faces')
    name = 'faces-update'
    lookup_field = "id"

    def perform_update(self, serializer):
         # Save the instance first
        instance = serializer.save()
        # Generate face encoding asynchronously
        generate_face_encoding_async(instance.id)

class DeleteFaces(generics.DestroyAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='delete_faces')
    name = 'delete-faces'
    lookup_field = "id"

class CreateFaces(generics.CreateAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='add_faces')
    name = 'create-faces'
    
    def perform_create(self, serializer):
        # Save the instance first
        instance = serializer.save()
        # Generate face encoding asynchronously
        generate_face_encoding_async(instance.id)
       


# ============================================================================
# FACE RECOGNITION WITH STREAMING AND BACKGROUND TASK SUPPORT
# ============================================================================

class FaceEncodingCache:
    """Efficient cache for face encodings using pickle serialization"""
    CACHE_KEY = "face_encodings_cache"
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @staticmethod
    def load_all_encodings():
        """Load all face encodings from cache or database"""
        cached_encodings = cache.get(FaceEncodingCache.CACHE_KEY)
        
        if cached_encodings is not None:
            return cached_encodings
        
        # Load from database
        faces = Faces.objects.filter(faceEncoding__isnull=False)
        encodings_data = {}
        
        for face in faces:
            try:
                # Ensure faceEncoding is bytes before unpickling
                face_encoding = face.faceEncoding
                if isinstance(face_encoding, str):
                    # Handle case where encoding was incorrectly stored as string
                    logger.warning(f"Face {face.id} encoding stored as string, attempting to convert")
                    face_encoding = face_encoding.encode('latin-1')
                
                # Deserialize pickle encoding
                encoding = pickle.loads(face_encoding)
                encodings_data[face.id] = {
                    'encoding': encoding,
                    'person_id': face.personId.id,
                    'person_name': f"{face.personId.firstName} {face.personId.lastName}",
                    'face_id': face.id
                }
            except Exception as e:
                logger.error(f"Error loading encoding for face {face.id}: {str(e)}")
                continue
        
        # Cache the encodings
        cache.set(FaceEncodingCache.CACHE_KEY, encodings_data, FaceEncodingCache.CACHE_TIMEOUT)
        return encodings_data
    
    @staticmethod
    def clear_cache():
        """Clear the encoding cache"""
        cache.delete(FaceEncodingCache.CACHE_KEY)


class FaceRecognitionEngine:
    """Efficient face recognition engine using numpy operations"""
    
    # Tolerance for face comparison (lower = stricter matching)
    # Standard face_recognition library uses 0.6, but we use stricter threshold
    # to reduce false positives (e.g., detecting clothes/patterns as faces)
    DISTANCE_THRESHOLD = 0.4  # Stricter than default 0.6
    
    # Minimum confidence for a face to be considered valid
    MIN_CONFIDENCE = 0.75
    
    @staticmethod
    def is_valid_face_region(image_array, face_location):
        """
        Validate that a detected region is actually a face, not clothing/patterns
        
        Args:
            image_array: Full image as numpy array
            face_location: tuple of (top, right, bottom, left) pixel coordinates
            
        Returns:
            bool: True if likely a face, False if likely false positive
        """
        try:
            top, right, bottom, left = face_location
            
            # Validate location is reasonable
            height = bottom - top
            width = right - left
            
            if height < 20 or width < 20:
                return False  # Too small to be a face
            
            # Extract face region
            face_region = image_array[top:bottom, left:right]
            
            if len(face_region.shape) == 3:
                gray = np.mean(face_region, axis=2)
            else:
                gray = face_region
            
            # Check for reasonable variance (faces have varied lighting)
            variance = np.var(gray)
            if variance < 100:  # Too uniform, likely solid color clothing
                return False
            
            # Check for skin tone concentration (rough check)
            # Typical skin RGB has high R, medium G, low B in normalized space
            if len(image_array.shape) == 3:
                r_channel = face_region[:,:,0].mean()
                g_channel = face_region[:,:,1].mean()
                b_channel = face_region[:,:,2].mean()
                
                # Very rough heuristic: face regions often have R > B
                # and not overly saturated single colors
                total = r_channel + g_channel + b_channel
                if total > 0:
                    r_ratio = r_channel / total
                    # If too blue or too monochrome, likely not a face
                    if r_ratio < 0.25:
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error validating face region: {str(e)}")
            return True  # Assume valid if validation fails
    
    @staticmethod
    def _generate_simple_encoding(image_array):
        """
        Generate a simple face encoding using image features when face_recognition is unavailable
        This is a fallback method that uses image statistics - no external dependencies
        
        Args:
            image_array: numpy array of image data
            
        Returns:
            numpy array representing image features
        """
        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray = np.mean(image_array, axis=2)
            else:
                gray = image_array
            
            # Create a simplified feature vector from image statistics
            features = []
            
            # Histogram features (divide into 4x4 grid, get mean for each)
            h, w = gray.shape
            grid_h, grid_w = max(1, h // 4), max(1, w // 4)
            
            for i in range(4):
                for j in range(4):
                    region = gray[i*grid_h:(i+1)*grid_h, j*grid_w:(j+1)*grid_w]
                    if region.size > 0:
                        features.append(np.mean(region))
                        features.append(np.std(region))
            
            # Add simple edge detection using numpy (no scipy needed)
            # Compute horizontal and vertical gradients
            gy = gray[1:, :] - gray[:-1, :]  # vertical edges
            gx = gray[:, 1:] - gray[:, :-1]  # horizontal edges
            edge_magnitude = np.sqrt(gy[:, :-1]**2 + gx[:-1, :]**2)
            
            features.append(np.mean(edge_magnitude))
            features.append(np.std(edge_magnitude))
            
            # Add overall statistics
            features.extend([
                np.mean(gray),
                np.std(gray),
                np.min(gray),
                np.max(gray)
            ])
            
            # Normalize to 128D vector for compatibility
            encoding = np.array(features, dtype=np.float32)
            if len(encoding) < 128:
                padding = np.zeros(128 - len(encoding), dtype=np.float32)
                encoding = np.concatenate([encoding, padding])
            else:
                encoding = encoding[:128]
            
            return encoding / np.linalg.norm(encoding)
        except Exception as e:
            logger.error(f"Error generating simple encoding: {str(e)}")
            return None
    
    @staticmethod
    def generate_face_encoding(image_array):
        """
        Generate face encoding from image array
        
        Args:
            image_array: numpy array of image data
            
        Returns:
            tuple: (encoding array, success boolean)
        """
        if FACE_RECOGNITION_AVAILABLE:
            try:
                # Detect faces in image
                face_locations = face_recognition.face_locations(image_array, model='hog')
                
                if not face_locations:
                    return None, False
                
                # Validate detected face is actually a face, not clothing/patterns
                valid_faces = [loc for loc in face_locations 
                              if FaceRecognitionEngine.is_valid_face_region(image_array, loc)]
                
                if not valid_faces:
                    logger.warning(f"Detected {len(face_locations)} faces but all failed validation")
                    return None, False
                
                # Generate encoding for the first valid detected face
                face_encodings = face_recognition.face_encodings(image_array, valid_faces)
                
                if face_encodings:
                    return face_encodings[0], True
                
                return None, False
            except Exception as e:
                logger.error(f"Error generating face encoding with face_recognition: {str(e)}")
                return None, False
        else:
            # Fallback to simple encoding when face_recognition is not available
            logger.warning("face_recognition not available, using fallback method")
            try:
                encoding = FaceRecognitionEngine._generate_simple_encoding(image_array)
                if encoding is not None:
                    return encoding, True
                return None, False
            except Exception as e:
                logger.error(f"Error in fallback face encoding: {str(e)}")
                return None, False
    
    @staticmethod
    def compare_faces_efficient(test_encoding, known_encodings_dict):
        """
        Efficiently compare test encoding against known encodings using numpy
        
        Args:
            test_encoding: numpy array of test face encoding
            known_encodings_dict: dict with encoding data
            
        Returns:
            list: Sorted list of matches with scores
        """
        if test_encoding is None or not known_encodings_dict:
            return []
        
        matches = []
        
        # Vectorized distance computation
        for face_id, data in known_encodings_dict.items():
            known_encoding = data['encoding']
            
            # Compute euclidean distance
            distance = np.linalg.norm(test_encoding - known_encoding)
            
            # Check if distance is below threshold AND confidence is high enough
            is_match = distance < FaceRecognitionEngine.DISTANCE_THRESHOLD
            confidence = float(1 - (distance / FaceRecognitionEngine.DISTANCE_THRESHOLD)) if is_match else 0.0
            
            # Additional check: only accept if confidence is above minimum
            if is_match and confidence < FaceRecognitionEngine.MIN_CONFIDENCE:
                is_match = False
                confidence = 0.0
            
            matches.append({
                'face_id': face_id,
                'person_id': data['person_id'],
                'person_name': data['person_name'],
                'distance': float(distance),
                'is_match': is_match,
                'confidence': confidence
            })
        
        # Sort by distance (closest first)
        matches.sort(key=lambda x: x['distance'])
        
        return matches
    
    @staticmethod
    def process_image_stream(image_data):
        """
        Process image from stream and convert to numpy array
        
        Args:
            image_data: bytes or file object
            
        Returns:
            tuple: (numpy array, success boolean)
        """
        try:
            # Handle different input types
            if isinstance(image_data, bytes):
                image_file = io.BytesIO(image_data)
            else:
                image_file = image_data
            
            # Open and convert image
            image = Image.open(image_file).convert('RGB')
            image_array = np.array(image)
            
            return image_array, True
        except Exception as e:
            logger.error(f"Error processing image stream: {str(e)}")
            return None, False

def mark_attendance(all_matches, request):
     # first closest match
            person_data = all_matches[0]
            person_id = person_data['person_id']
            
            # Get the Person instance
            try:
                person = Person.objects.get(id=person_id)
            except Person.DoesNotExist:
                return Response(
                    {
                        'success': False,
                        'error': f'Person with ID {person_id} not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get service ID from request
            service_id_value = request.data.get('serviceId') if request.data else None
            
            # Create attendance record
            try:
                capture_method = CaptureMethod.objects.get(method='FACE')
            except CaptureMethod.DoesNotExist:
                logger.warning("FACE capture method not found, creating attendance without it")
                capture_method = None
            
            # Get the Services instance if serviceId is provided
            services = None
            if service_id_value:
                try:
                    from services.models import Services
                    services = Services.objects.get(id=service_id_value)
                except Services.DoesNotExist:
                    logger.warning(f"Services with ID {service_id_value} not found")
                    services = None
            
            # Only create attendance if we have a services instance (required field)
            if services:
                attendance = Attendance.objects.create(
                    personId=person,
                    servicesId=services,
                    comment='Checked in via face recognition',
                    captureMethodId=capture_method if capture_method else None
                )
                attendance.save()
            attendance.save()

class FaceRecognitionStreamView(APIView):
    """
    API view for real-time face recognition from image streams
    
    POST: Stream image and perform face recognition
    Expects multipart/form-data with 'image' field containing image file
    """
    permission_classes = [AllowAny]
    #required_groups = requiredGroups(permission='view_faces')

    def post(self, request):
        """
        Perform face recognition on streamed image
        
        Request body:
        - image: Image file (required)
        - serviceId: service identifier
        
        Response:
        {
            "success": true,
        }
        """
        
        try:
            # Validate request
            if 'image' not in request.FILES:
                return Response(
                    {
                        'success': False,
                        'error': 'Image file is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            image_bytes = image_file.read()
            
            # Process image stream
            image_array, success = FaceRecognitionEngine.process_image_stream(image_bytes)
            
            if not success:
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to process image'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate face encoding
            test_encoding, success = FaceRecognitionEngine.generate_face_encoding(image_array)
            
            if not success:
                return Response(
                    {
                        'success': False,
                        'error': 'No face detected in image'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Load all known encodings (cached)
            known_encodings = FaceEncodingCache.load_all_encodings()
            
            if not known_encodings:
                return Response(
                    {
                        'success': False,
                        'error': 'No face data available in database'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Perform face comparison
            all_matches = FaceRecognitionEngine.compare_faces_efficient(
                test_encoding,
                known_encodings
            )
            
            if not all_matches:
                return Response(
                    {'success': False},
                    status=status.HTTP_404_NOT_FOUND
                )
            # if there are matches mark attendance for the first closest match
            mark_attendance(all_matches, request)
            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in face recognition: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f'Face recognition error: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class CacheManagementView(APIView):
    """
    Manage face encoding cache
    """
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def post(self, request):
        """
        Clear or reload face encoding cache
        
        Query params:
        - action: 'clear' or 'reload'
        """
        action = request.data.get('action', 'reload')
        
        try:
            if action == 'clear':
                FaceEncodingCache.clear_cache()
                return Response({
                    'success': True,
                    'message': 'Face encoding cache cleared'
                }, status=status.HTTP_200_OK)
            
            elif action == 'reload':
                FaceEncodingCache.clear_cache()
                encodings = FaceEncodingCache.load_all_encodings()
                return Response({
                    'success': True,
                    'message': 'Face encoding cache reloaded',
                    'encodings_loaded': len(encodings)
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid action. Use "clear" or "reload"'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error managing cache: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)