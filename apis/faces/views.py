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
from django.http import HttpResponse
from rest_framework.views import APIView
from role.util import requiredGroups
from user.permissions import IsInGroup
import numpy as np
from PIL import Image
import io
import hashlib
import pickle
from attendance.models import Attendance
from capturemethod.models import CaptureMethod
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)



#this generic class will handle GET method to be used by the admin alone
class FacesList(generics.ListAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_faces')
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
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_faces')
    name = 'faces-update'
    lookup_field = "id"

class DeleteFaces(generics.DestroyAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_faces')
    name = 'delete-faces'
    lookup_field = "id"

class CreateFaces(generics.CreateAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_faces')
    name = 'create-faces'
    
    def perform_create(self, serializer):
        # Save the instance first
        instance = serializer.save()
        
        # Generate face embeddings from the image fields
        embeddings_list = []
        image_fields = [instance.pics, instance.pics2, instance.pics3]
        
        for image_field in image_fields:
            if image_field:
                try:
                    # Read the image file
                    image_path = image_field.path
                    img = Image.open(image_path)
                    
                    # Resize to a standard size for consistency
                    img = img.resize((128, 128))
                    
                    # Convert to numpy array and normalize
                    img_array = np.array(img).flatten().astype(np.float32) / 255.0
                    embeddings_list.append(img_array)
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue
        
        # Combine embeddings (averaging them)
        if embeddings_list:
            # Handle different embedding sizes by resizing to average size
            max_len = max(len(e) for e in embeddings_list)
            padded_embeddings = []
            for e in embeddings_list:
                if len(e) < max_len:
                    # Pad with zeros if needed
                    padded = np.pad(e, (0, max_len - len(e)), 'constant')
                else:
                    padded = e[:max_len]
                padded_embeddings.append(padded)
            
            combined_embedding = np.mean(padded_embeddings, axis=0)
            # Convert numpy array to binary format
            face_encoding = combined_embedding.astype(np.float32).tobytes()
            # Save the binary encoding
            instance.faceEncoding = face_encoding
            instance.save()


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
                # Deserialize pickle encoding
                encoding = pickle.loads(face.faceEncoding)
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
    DISTANCE_THRESHOLD = 0.6
    
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
                
                # Generate encoding for the first detected face
                face_encodings = face_recognition.face_encodings(image_array, face_locations)
                
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
            
            is_match = distance < FaceRecognitionEngine.DISTANCE_THRESHOLD
            
            matches.append({
                'face_id': face_id,
                'person_id': data['person_id'],
                'person_name': data['person_name'],
                'distance': float(distance),
                'is_match': is_match,
                'confidence': float(1 - (distance / FaceRecognitionEngine.DISTANCE_THRESHOLD))
                if is_match else 0.0
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


class FaceRecognitionStreamView(APIView):
    """
    API view for real-time face recognition from image streams
    
    POST: Stream image and perform face recognition
    Expects multipart/form-data with 'image' field containing image file
    """
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='view_faces')
    
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
        import time
        start_time = time.time()
        
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
            
            # first closest match
            person = all_matches[0]
            # create attendance
            attendance = Attendance.objects.create(personId=person['person_id'], 
                                                   serviceId=request.data.get('serviceId'),
                                                   comment='Checked in via face recognition',
                                                   captureMethodId=CaptureMethod.objects.get(method='FACE').id)
            attendance.save()


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


class BatchFaceRecognitionView(APIView):
    """
    Batch face recognition for multiple images
    Processes images in parallel using ThreadPoolExecutor
    """
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='view_faces')
    
    def post(self, request):
        """
        Perform batch face recognition
        
        Request body:
        - images: Array of image files
        - serviceId:service identifier
        
        Response:
        {
            "success": true,
        }
        """
        
        try:
            image_files = request.FILES.getlist('images')
            
            if not image_files:
                return Response(
                    {
                        'success': False,
                        'error': 'No images provided'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Load encodings once
            known_encodings = FaceEncodingCache.load_all_encodings()
            
            results = []
            failed_count = 0
            
            # Process images in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for idx, image_file in enumerate(image_files):
                    future = executor.submit(
                        self._process_single_image,
                        idx,
                        image_file,
                        known_encodings,
                        request
                    )
                    futures.append(future)
                
                for future in futures:
                    result = future.result()
                    if result['success']:
                        results.append(result)
                    else:
                        failed_count += 1
            
            
            return Response({
                'success': True,
                'total_images': len(image_files),
                'processed': len(results),
                'failed': failed_count,
                'results': results,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in batch face recognition: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f'Batch processing error: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _process_single_image(idx, image_file, known_encodings, request):
        """Process a single image and return results"""
        try:
            image_bytes = image_file.read()
            
            # Process image
            image_array, success = FaceRecognitionEngine.process_image_stream(image_bytes)
            if not success:
                return {
                    'success': False,
                    'index': idx,
                    'filename': image_file.name,
                    'error': 'Failed to process image'
                }
            
            # Generate encoding
            test_encoding, success = FaceRecognitionEngine.generate_face_encoding(image_array)
            if not success:
                return {
                    'success': False,
                    'index': idx,
                    'filename': image_file.name,
                    'error': 'No face detected'
                }
            
            # Compare faces
            matches = FaceRecognitionEngine.compare_faces_efficient(
                test_encoding,
                known_encodings
            )
            
            # first closest match
            if matches:
               person = matches[0]
               # create attendance
               attendance = Attendance.objects.create(personId=person['person_id'], 
                                                   serviceId=request.data.get('serviceId'),
                                                   comment='Checked in via face recognition',
                                                   captureMethodId=CaptureMethod.objects.get(method='FACE').id)
               attendance.save()

            
            return {
                'success': True,
                'index': idx,
                'filename': image_file.name,
                'top_match': matches[0] if matches else None,
                'matches_found': len([m for m in matches if m['is_match']])
            }
            
        except Exception as e:
            logger.error(f"Error processing image {idx}: {str(e)}")
            return {
                'success': False,
                'index': idx,
                'filename': getattr(image_file, 'name', 'unknown'),
                'error': str(e)
            }


class CacheManagementView(APIView):
    """
    Manage face encoding cache
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
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