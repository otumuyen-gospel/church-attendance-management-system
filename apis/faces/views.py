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
from role.util import requiredGroups



#this generic class will handle GET method to be used by the admin alone
class FacesList(generics.ListAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [AllowAny,]
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
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='change_faces')
    name = 'faces-update'
    lookup_field = "id"

class DeleteFaces(generics.DestroyAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='delete_faces')
    name = 'delete-faces'
    lookup_field = "id"

class CreateFaces(generics.CreateAPIView):
    queryset = Faces.objects.all()
    serializer_class = FacesSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='add_faces')
    name = 'create-faces'