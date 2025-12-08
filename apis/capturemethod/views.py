from .models import CaptureMethod
from .serializers import CaptureMethodSerializers
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
from user.permissions import IsInGroup



#this generic class will handle GET method to be used by the admin alone
class CaptureMethodList(generics.ListAPIView):
    queryset = CaptureMethod.objects.all()
    serializer_class = CaptureMethodSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_capturemethod')
    name = 'capturemethod-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('method','description',) 

     #you can search using the "search" keyword
    search_fields = ('method','description',) 

    #you can order using the "ordering" keyword
    ordering_fields = ('method','description',) 


class UpdateCaptureMethod(generics.UpdateAPIView):
    queryset = CaptureMethod.objects.all()
    serializer_class = CaptureMethodSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_capturemethod')
    name = 'capturemethod-update'
    lookup_field = "id"

class DeleteCaptureMethod(generics.DestroyAPIView):
    queryset = CaptureMethod.objects.all()
    serializer_class = CaptureMethodSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_capturemethod')
    name = 'delete-capturemethod'
    lookup_field = "id"

class CreateCaptureMethod(generics.CreateAPIView):
    queryset = CaptureMethod.objects.all()
    serializer_class = CaptureMethodSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_capturemethod')
    name = 'create-capturemethod'