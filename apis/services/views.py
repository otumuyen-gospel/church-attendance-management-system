from .models import Services
from .serializers import ServicesSerializers
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
from django.contrib.auth.models import Group, Permission
from role.util import requiredGroups


#this generic class will handle GET method to be used by the admin alone
class ServicesList(generics.ListAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='view_services')
    name = 'services-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('eventName','eventDate','eventDay','eventTime','churchId__id', 'ministryId__id')  

     #you can search using the "search" keyword
    search_fields = ('eventName','eventDate','eventDay','eventTime','churchId__id', 'ministryId__id')

    #you can order using the "ordering" keyword
    ordering_fields = ('eventName','eventDate','eventDay','eventTime','churchId__id', 'ministryId__id') 


class UpdateServices(generics.UpdateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='change_services')
    name = 'services-update'
    lookup_field = "id"


class DeleteServices(generics.DestroyAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='delete_services')
    name = 'delete-services'
    lookup_field = "id"


class CreateServices(generics.CreateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='add_services')
    name = 'create-services'
    