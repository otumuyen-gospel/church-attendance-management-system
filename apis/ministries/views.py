from .models import Ministries
from .serializers import MinistriesSerializers
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
from user.permissions import IsInGroup


#this generic class will handle GET method to be used by the admin alone
class MinistriesList(generics.ListAPIView):
    queryset = Ministries.objects.all()
    serializer_class = MinistriesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_ministries')
    name = 'ministries-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('name','description','churchId__id')  

     #you can search using the "search" keyword
    search_fields = ('name','description','churchId__id')   

    #you can order using the "ordering" keyword
    ordering_fields = ('name','description','churchId__id') 


class UpdateMinistries(generics.UpdateAPIView):
    queryset = Ministries.objects.all()
    serializer_class = MinistriesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_ministries')
    name = 'ministries-update'
    lookup_field = "id"


class DeleteMinistries(generics.DestroyAPIView):
    queryset = Ministries.objects.all()
    serializer_class = MinistriesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_ministries')
    name = 'delete-ministries'
    lookup_field = "id"


class CreateMinistries(generics.CreateAPIView):
    queryset = Ministries.objects.all()
    serializer_class = MinistriesSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_ministries')
    name = 'create-ministries'
    