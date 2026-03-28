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

import concurrent.futures
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .cache import FacesCache
from attendance.models import Attendance
from services.models import Services
from capturemethod.models import CaptureMethod
from django.utils import timezone


def process_image_encoding(file):
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


class UpdateFaces(generics.GenericAPIView):
    serializer_class = CreateFaceSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='change_faces')
    name = 'faces-update'
    
    def post(self, request, *args, **kwargs):
        #Get Person
        personId = Person.objects.get(id=request.data.get('personId'))
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
            return Response({"error": "All 5 images must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        

        # Process images in parallel for better performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {executor.submit(process_image_encoding, file): file for file in image_files}
            all_encodings = []
            for future in concurrent.futures.as_completed(future_to_file):
                encoding = future.result()
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

        # Invalidate cache to refresh with updated face
        FacesCache.invalidate_cache()
        
        return Response({
            "message": f"Face updated for {personId.firstName} {personId.lastName}",
            "encodings": avg_encoding
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

    def post(self, request, *args, **kwargs):
        #Get Person
        personId = Person.objects.get(id=request.data.get('personId'))
        if not personId:
            return Response({"error": "Person with the provided ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if Faces.objects.filter(personId=personId).exists():
            return Response({"error": "A face record already exists for this person."}, status=status.HTTP_400_BAD_REQUEST)

        # Load and encode
        frontview = self.request.FILES.get('frontview')
        leftsideview = self.request.FILES.get('leftsideview')
        rightsideview = self.request.FILES.get('rightsideview')
        smileview = self.request.FILES.get('smileview')
        frownview = self.request.FILES.get('frownview')
        image_files = [frontview, leftsideview, rightsideview, smileview, frownview]
        if not all(image_files):
            return Response({"error": "All 5 images must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        

        # Process images in parallel for better performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {executor.submit(process_image_encoding, file): file for file in image_files}
            all_encodings = []
            for future in concurrent.futures.as_completed(future_to_file):
                encoding = future.result()
                if encoding is not None:
                    all_encodings.append(encoding)

        if not all_encodings:
            return Response({"error": "No faces detected in any of the provided images"}, status=status.HTTP_400_BAD_REQUEST)

        # Average the encodings for better accuracy
        avg_encoding = np.mean(all_encodings, axis=0).tolist()
        #create new face record for the person
        Faces.objects.create(
            personId=personId,
            encoding=avg_encoding,
            pics=frontview
        )

        # Invalidate cache to refresh with new face
        FacesCache.invalidate_cache()

        return Response({
            "message": f"Face registered for {personId.firstName} {personId.lastName}",
            "encodings": avg_encoding
        }, status=status.HTTP_201_CREATED)



class RecognizeFaceView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsInGroup]
    serializer_class = RecognizeFaceSerializer
    required_groups = requiredGroups(permission='view_faces')

    def capture_attendance(self, personID, servicesId, faceMatchDistance, match= True):
        try:
            person = Person.objects.get(id=personID)
            services = Services.objects.get(id=servicesId)
            capture_method = CaptureMethod.objects.get(method=CaptureMethod.METHOD_FACE)
            
            today = timezone.now().date()
            
            # Check if already attended today
            if Attendance.objects.filter(personId=person, attendanceDate=today, servicesId=services).exists():
                return Response({
                    "message": f"{person.firstName} {person.lastName} has already been marked present for today"
                }, status=status.HTTP_200_OK)
            
            # Create attendance record
            Attendance.objects.create(
                personId=person,
                servicesId=services,
                captureMethodId=capture_method
            )
            
            return Response({
                "message": f"Attendance successfully captured for {person.firstName} {person.lastName}",
                "person": f"{person.firstName} {person.lastName}",
                "service": services.eventName,
                "date": today,
                "faceMatchDistance" :faceMatchDistance,
                "match": True
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

        # Load uploaded image
        img = face_recognition.load_image_file(file)
        unknown_encodings = face_recognition.face_encodings(img, num_jitters=10)

        if not unknown_encodings:
            return Response({"message": "Please upload an image with a face"}, status=status.HTTP_404_NOT_FOUND)

        unknown_encoding = unknown_encodings[0]

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
            return self.capture_attendance(person.id, services_id, float(face_distances[best_match_index]))

        return Response({"match": False, "message": "Unknown person(face not recognized)"}, status=status.HTTP_404_NOT_FOUND)