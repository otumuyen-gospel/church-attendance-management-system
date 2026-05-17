import os
import tempfile

from django.shortcuts import render
from fontTools import encodings
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from role.util import requiredGroups
from user.permissions import IsInGroup
from .models import Faces
from person.models import Person
from .serializers import FacesSerializers, RecognizeFaceSerializer, CreateFaceSerializer

import numpy as np
from faces.apps import FacesConfig
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from rest_framework.response import Response
from rest_framework import status

from .cache import FacesCache
from attendance.models import Attendance
from services.models import Services
from capturemethod.models import CaptureMethod
from django.utils import timezone

storage = FacesConfig.storage

class FacesList(generics.ListAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
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
    required_groups = requiredGroups(permission='add_faces')
    name='cache-faces'
    def post(self, request, *args, **kwargs):
        # Get all Faces from database
        faces = Faces.objects.all()
        if not faces.exists():
            return Response({"message": "No faces found in database to cache"}, status=status.HTTP_404_NOT_FOUND)
        # Clear existing cache and load fresh data from database
        FacesCache.refresh_cache()
        return Response({"message": "Faces cache refreshed successfully"}, status=status.HTTP_200_OK)

class UpdateFaceView(generics.GenericAPIView):
    serializer_class = CreateFaceSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='change_faces')
    name = 'faces-update'
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_update(serializer)
    def perform_update(self, serializer):
        personId = serializer.validated_data.get('personId')
        persons = Person.objects.filter(id=personId)
        if not persons.exists():
            return Response({"error": "Person with the provided ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        face = Faces.objects.filter(personId=personId)
        if not face.exists():
            return Response({"error": "No existing face record found for this person."}, status=status.HTTP_404_NOT_FOUND)
        
        person = persons.first()
        face = face.first()

        #get uploaded files
        pics = serializer.validated_data.get('frontview')
        image_files= [
            pics,
            serializer.validated_data.get('leftsideview'),
            serializer.validated_data.get('rightsideview'),
            serializer.validated_data.get('smileview'),
            serializer.validated_data.get('frownview')
        ]

        # encode and uplaod faces data
         # Process images sequentially 
        all_encodings = []
        for file in image_files:
           encoding= FacesConfig.face_handler.get_embedding(file.read())
           if encoding is not None:
               all_encodings.append(encoding)

        if not all_encodings:
            return Response({"error": "No faces detected in any of the provided images"}, status=status.HTTP_400_BAD_REQUEST)

        # Average the encodings for better accuracy
        master_encoding = np.mean(np.array(all_encodings), axis=0)
        
        # Normalize the averaged vector (Crucial for cosine similarity)
        master_encoding = master_encoding / np.linalg.norm(master_encoding)

        #update existing face record for the person
        if pics:
            pics.seek(0)
            new_path = storage.update_file(str(face.pics), pics)
            if new_path:
                face.pics = new_path
                face.encoding=master_encoding.tolist()
                face.save()
            else:
                return Response({"error":"Failed to update face"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"Failed to upload Front View image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": f"Face updated for {person.firstName} {person.lastName}",
        }, status=status.HTTP_201_CREATED)


class CreateFaceView(generics.GenericAPIView):
    serializer_class = CreateFaceSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='add_faces')
    name = 'faces-create'
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializer)
    def perform_create(self, serializer):
        personId = serializer.validated_data.get('personId')
        persons = Person.objects.filter(id=personId)
        if not persons.exists():
            return Response({"error": "Person with the provided ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        face = Faces.objects.filter(personId=personId)
        if face.exists():
            return Response({"error": "Face record already exists for this person."}, status=status.HTTP_400_BAD_REQUEST)

        person = persons.first()

        #get uploaded files
        pics = serializer.validated_data.get('frontview')
        image_files= [
            pics,
            serializer.validated_data.get('leftsideview'),
            serializer.validated_data.get('rightsideview'),
            serializer.validated_data.get('smileview'),
            serializer.validated_data.get('frownview')
        ]

        # encode and upload faces data
         # Process images sequentially 
        all_encodings = []
        for file in image_files:
           encoding= FacesConfig.face_handler.get_embedding(file.read())
           if encoding is not None:
               all_encodings.append(encoding)

        if not all_encodings:
            return Response({"error": "No faces detected in any of the provided images"}, status=status.HTTP_400_BAD_REQUEST)

        # Average the encodings for better accuracy
        master_encoding = np.mean(np.array(all_encodings), axis=0)
        
        # Normalize the averaged vector (Crucial for cosine similarity)
        master_encoding = master_encoding / np.linalg.norm(master_encoding)

        #update existing face record for the person
        if pics:
            pics.seek(0)
            new_path = storage.upload_file(pics)
            if new_path:
                Faces.objects.create(personId=person, 
                                     pics=new_path,
                                     encoding=master_encoding.tolist())
            else:
                return Response({"error":"Failed to upload face"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"Failed to upload Front View image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": f"Face uploaded for {person.firstName} {person.lastName}",
        }, status=status.HTTP_201_CREATED)


class DeleteFaces(generics.DestroyAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='delete_faces')
    name = 'delete-faces'
    lookup_field = "id"

    def perform_destroy(self, instance):
       if instance.pics:
          storage.delete_file(str(instance.pics))

       return super().perform_destroy(instance)
    
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
        services = Services.objects.filter(id=services_id)
        if not services.exists():
            return Response({"error":"this service does not exist"},status=status.HTTP_404_NOT_FOUND)
        service = services.first()
        if service.eventDate != timezone.now().date() and service.eventDay != timezone.now().strftime('%a').upper():
            return Response({"message" : f"Attendance can only be captured for today's services. The event date for {services.eventName} is {services.eventDate} {services.eventDay} {services.eventTime}."})

        # Load uploaded image and get encoding and normalize it
        unknown_encoding = FacesConfig.face_handler.get_embedding(file.read())
        if not unknown_encoding:
            return Response({"message": "Please upload an image with a face"}, status=status.HTTP_404_NOT_FOUND)

        # Get all known faces from cache
        known_encodings = FacesCache.get_all_encodings()
        known_face_ids = FacesCache.get_face_ids()

        if not known_encodings:
            return Response({"message": "No known faces in database(cache is empty)"}, status=status.HTTP_404_NOT_FOUND)
        # Compare faces
        best_index, score = FacesConfig.face_handler.find_best_match(known_encodings, unknown_encoding)
        if best_index is not None and score >= 0.4: # Threshold for a match:
            matched_face_id = known_face_ids[best_index]
            matched_face = Faces.objects.get(id=matched_face_id)
            person = matched_face.personId
            # Capture attendance
            return self.capture_attendance(person.id, service, float(score))

        return Response({"match": False, "message": "Unknown person(face not recognized)"}, status=status.HTTP_404_NOT_FOUND)





