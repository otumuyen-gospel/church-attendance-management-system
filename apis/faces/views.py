import os
import tempfile

from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from role.util import requiredGroups
from user.permissions import IsInGroup
from .models import Faces
from person.models import Person
from .serializers import FacesSerializers, RecognizeFaceSerializer, CreateFaceSerializer

import face_recognition
import numpy as np
import cv2
from mtcnn_cv2 import MTCNN
import mediapipe as mp
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from rest_framework.response import Response
from rest_framework import status

from .cache import FacesCache
from attendance.models import Attendance
from services.models import Services
from capturemethod.models import CaptureMethod
from django.utils import timezone

'''
####### OLD ENCODING FUNCTIONS - KEPT FOR REFERENCE #######
#slower but more accurate encoding by not resizing image and using num_filter=10
def process_image_encoding(file):
    if isinstance(file, InMemoryUploadedFile):
      pass # file is already in mmory no need to save to disk
    elif isinstance(file, TemporaryUploadedFile):
      file = file.temporary_file_path()

    """
    Process a single image file to get face encoding.
    Returns the encoding or None if no face found.
    """
    try:
        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img, num_jitters=10)
        return encodings[0] if encodings else None
    except Exception:
        return None

#faster but less accurate encoding by resizing image and using num_filter=1
def process_image_encoding_2(file):
    # 1. Faster Image Load
    img = cv2.imread(file.temporary_file_path())
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 2. Resize frame
    small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)

    # 3. Use faster detection + reduced jitters
    face_locations = face_recognition.face_locations(small_frame)
    # num_jitters=1 is much faster than 10
    encodings = face_recognition.face_encodings(small_frame, face_locations, num_jitters=1)
    return encodings[0] if encodings else None
'''

# faster and more accurate
def process_image_encoding_3(file):
  if isinstance(file, InMemoryUploadedFile):
      pass # file is already in mmory no need to save to disk
  elif isinstance(file, TemporaryUploadedFile):
      file = file.temporary_file_path()

  # 1. Initialize detector and load image
  detector = MTCNN(min_face_size= 80)
  full_image = face_recognition.load_image_file(file)

  # 2. Resizing Logic: Scale down for speed (0.25 = 1/4 size)
  scale_factor = 0.25
  small_image = cv2.resize(full_image, (0, 0), fx=scale_factor, fy=scale_factor)

  # 3. Detect faces on the smaller image
  results = detector.detect_faces(small_image)

  # 4. Map locations back to original scale
  face_locations = []
  for res in results:
     x, y, w, h = res['box']
    
     # Scale coordinates back up (divide by scale_factor)
     top = int(y / scale_factor)
     right = int((x + w) / scale_factor)
     bottom = int((y + h) / scale_factor)
     left = int(x / scale_factor)
    
     face_locations.append((top, right, bottom, left))

  # 5. Encode using the original full-resolution image
  # This ensures accuracy isn't lost during the recognition phase
  encodings = face_recognition.face_encodings(full_image, known_face_locations=face_locations, num_jitters=1)
  return encodings[0] if encodings else None


class FacesList(generics.ListAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_faces')
    name = 'faces-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filter by field names
    filterset_fields = ('personId__id',)

    # Search using the "search" keyword
    search_fields = ('personId__id',)

    # Order using the "ordering" keyword
    ordering_fields = ('personId__id',)


class CacheFaces(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsInGroup]
    reuired_groups = requiredGroups(permission='add_faces')
    name='cache-faces'
    def post(self, request, *args, **kwargs):
        # Get all Faces from database
        faces = Faces.objects.all()
        if not faces.exists():
            return Response({"message": "No faces found in database to cache"}, status=status.HTTP_404_NOT_FOUND)
        # Clear existing cache and load fresh data from database
        FacesCache.refresh_cache()
        return Response({"message": "Faces cache refreshed successfully"}, status=status.HTTP_200_OK)

class UpdateFaces(generics.GenericAPIView):
    serializer_class = CreateFaceSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='change_faces')
    name = 'faces-update'
    
    def post(self, request, *args, **kwargs):
        #Get request data
        id = self.request.data.get('personId')
        if not id:
            return Response({"error": "personId is required"}, status=status.HTTP_400_BAD_REQUEST)
        personId = Person.objects.get(id=id)
        if not personId:
            return Response({"error": "Person with the provided ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        face = Faces.objects.filter(personId=personId)
        if not face.exists():
            return Response({"error": "No existing face record found for this person."}, status=status.HTTP_404_NOT_FOUND)
        
        # Load and encode
        frontview = self.request.FILES.get('frontview')
        leftsideview = self.request.FILES.get('leftsideview')
        rightsideview = self.request.FILES.get('rightsideview')
        smileview = self.request.FILES.get('smileview')
        frownview = self.request.FILES.get('frownview')
        image_files = [frontview, leftsideview, rightsideview, smileview, frownview]
        if not all(image_files):
            return Response({"error": "frontview, leftsideview, rightsideview, smileview(smiling), and frownview(frowning) of user face are all required"}, status=status.HTTP_400_BAD_REQUEST)
        

         # Process images sequentially 
        all_encodings = []
        for file in image_files:
           encoding= process_image_encoding_3(file)
           if encoding is not None:
               all_encodings.append(encoding)

        if not all_encodings:
            return Response({"error": "No faces detected in any of the provided images"}, status=status.HTTP_400_BAD_REQUEST)

        # Average the encodings for better accuracy
        avg_encoding = np.mean(all_encodings, axis=0).tolist()
        #update existing face record for the person
        face = face.first()
        face.encoding=avg_encoding
        face.pics=frontview
        face.save()
        
        return Response({
            "message": f"Face updated for {personId.firstName} {personId.lastName}",
        }, status=status.HTTP_201_CREATED)


class DeleteFaces(generics.DestroyAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='delete_faces')
    name = 'delete-faces'
    lookup_field = "id"

class CreateFaces(generics.GenericAPIView):
    serializer_class = CreateFaceSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='add_faces')
    name = 'create-faces'
    def post(self,request, *args, **kwargs):
        #Get request data
        id = self.request.data.get('personId')
        if not id:
            return Response({"error": "personId is required"}, status=status.HTTP_400_BAD_REQUEST)
        personId = Person.objects.get(id=id)
        if not personId:
            return Response({"error": "Person with the provided ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if Faces.objects.filter(personId=personId).exists():
            return Response({"error": "A face record already exists for this person."}, status=status.HTTP_400_BAD_REQUEST)

        # upload face views
        frontview = self.request.FILES.get('frontview')
        leftsideview = self.request.FILES.get('leftsideview')
        rightsideview = self.request.FILES.get('rightsideview')
        smileview = self.request.FILES.get('smileview')
        frownview = self.request.FILES.get('frownview')
        image_files = [frontview, leftsideview, rightsideview, smileview, frownview]
        if not all(image_files):
            return Response({"error": "frontview, leftsideview, rightsideview, smileview(smiling), and frownview(frowning) of user face are all required"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Process images sequentially 
        all_encodings = []
        for file in image_files:
           encoding = process_image_encoding_3(file)
           if encoding is not None:
               all_encodings.append(encoding)

        if not all_encodings:
            return Response({"error": "No faces detected in any of the provided images"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Average the encodings for better accuracy
        avg_encoding = np.mean(all_encodings, axis=0).tolist()

        #create new face record for the person
        Faces.objects.create(personId=personId, encoding=avg_encoding, pics=frontview)
    
        return Response({
            "message": f"Face created for {personId.firstName} {personId.lastName}",
        }, status=status.HTTP_201_CREATED)



class RecognizeFaceView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsInGroup]
    serializer_class = RecognizeFaceSerializer
    required_groups = requiredGroups(permission='add_attendance')

    def capture_attendance(self, personID, services, faceMatchDistance, match= True):
        try:
            person = Person.objects.get(id=personID)
            capture_method = CaptureMethod.objects.get(method=CaptureMethod.METHOD_FACE)
            
            today = timezone.now().date()
            
            # Check if already attended today
            if Attendance.objects.filter(personId=person, attendanceDate=today, servicesId=services).exists():
                return Response({
                    "message": f"{person.firstName} {person.lastName} has already been marked present for today's {services.eventName}"
                }, status=status.HTTP_200_OK)
            
            # Create attendance record
            Attendance.objects.create(
                personId=person,
                servicesId=services,
                captureMethodId=capture_method,
                comment = capture_method.description
            )
            
            return Response({
                "message": f"Attendance successfully captured for {person.firstName} {person.lastName}",
                "person": f"{person.firstName} {person.lastName}",
                "service": services.eventName,
                "date": today,
                "faceMatchDistance" :faceMatchDistance,
                "match": match
            }, status=status.HTTP_201_CREATED)
            
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
        except Services.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
        except CaptureMethod.DoesNotExist:
            return Response({"error": "Face capture method not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['pics']
        services_id = serializer.validated_data['servicesId']
        services = Services.objects.get(id=services_id)
        if services.eventDate != timezone.now().date() and services.eventDay != timezone.now().strftime('%a').upper():
            return Response({"message" : f"Attendance can only be captured for today's services. The event date for {services.eventName} is {services.eventDate} {services.eventDay} {services.eventTime}."})

        # Load uploaded image and get encoding
        unknown_encoding = process_image_encoding_3(file)
        if not unknown_encoding.any():
            return Response({"message": "Please upload an image with a face"}, status=status.HTTP_404_NOT_FOUND)

        # Get all known faces from cache
        known_encodings = FacesCache.get_all_encodings()
        known_names = FacesCache.get_face_names()
        known_face_ids = FacesCache.get_face_ids()

        if not known_encodings:
            return Response({"message": "No known faces in database(cache is empty)"}, status=status.HTTP_404_NOT_FOUND)

        # Compare
        results = face_recognition.compare_faces(known_encodings, unknown_encoding,tolerance=0.4)
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)

        best_match_index = np.argmin(face_distances)
        if results[best_match_index]:
            matched_face_id = known_face_ids[int(best_match_index)]
            matched_face = Faces.objects.get(id=matched_face_id)
            person = matched_face.personId
            # Capture attendance
            return self.capture_attendance(person.id, services, float(face_distances[best_match_index]))

        return Response({"match": False, "message": "Unknown person(face not recognized)"}, status=status.HTTP_404_NOT_FOUND)