from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from role.util import requiredGroups
from user.permissions import IsInGroup

from .models import Faces
from .serializers import FacesSerializers


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
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='add_faces')
    name = 'create-faces'