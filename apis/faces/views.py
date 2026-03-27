from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from role.util import requiredGroups
from user.permissions import IsInGroup
from .models import Faces
from .serializers import FacesSerializers, RecognizeFaceSerializer

import face_recognition
import numpy as np

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import io
from PIL import Image


class FacesList(generics.ListAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [AllowAny]
    name = 'faces-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filter by field names
    filterset_fields = ('personId__id',)

    # Search using the "search" keyword
    search_fields = ('personId__id',)

    # Order using the "ordering" keyword
    ordering_fields = ('personId__id',)


class UpdateFaces(generics.UpdateAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='change_faces')
    name = 'faces-update'
    lookup_field = "id"


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
    permission_classes = [AllowAny]
    #required_groups = requiredGroups(permission='add_faces')
    name = 'create-faces'

    def perform_create(self, serializer):
        # Load and encode
        img = face_recognition.load_image_file(self.request.FILES['pics'])
        encodings = face_recognition.face_encodings(img)

        if not encodings:
            return Response({"error": "No face detected in image"}, status=status.HTTP_400_BAD_REQUEST)

        # Save encoding as list (JSON serializable)
        encodings = encodings[0].tolist()
        
        serializer.save(encoding=encodings)


class RecognizeFaceView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecognizeFaceSerializer
    #required_groups = requiredGroups(permission='view_faces')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['pics']

        # Load uploaded image
        img = face_recognition.load_image_file(file)
        unknown_encodings = face_recognition.face_encodings(img)

        if not unknown_encodings:
            return Response({"message": "Please upload an image with a face"}, status=status.HTTP_404_NOT_FOUND)

        unknown_encoding = unknown_encodings[0]

        # Get all known faces from DB
        known_faces = Faces.objects.all()
        known_encodings = [np.array(face.encoding) for face in known_faces if face.encoding]
        known_names = [f"{face.personId.firstName} {face.personId.lastName}" for face in known_faces]

        if not known_encodings:
            return Response({"message": "No known faces in database(database is empty)"}, status=status.HTTP_404_NOT_FOUND)

        # Compare
        results = face_recognition.compare_faces(known_encodings, unknown_encoding)
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)

        best_match_index = np.argmin(face_distances)
        if results[best_match_index]:
            name = known_names[best_match_index]
            return Response({"match": True, "name": name, "distance": float(face_distances[best_match_index])})

        return Response({"match": False, "message": "Unknown person(face not recognized)"})
        