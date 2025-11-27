from .models import Role
from .serializers import RoleSerializers
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



#this generic class will handle GET method to be used by the admin alone
class RoleList(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    name = 'role-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('name','description',)  

     #you can search using the "search" keyword
    search_fields = ('name','description',)   

    #you can order using the "ordering" keyword
    ordering_fields = ('name','description',) 


class UpdateRole(generics.UpdateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    name = 'role-update'
    lookup_field = "id"

class DeleteRole(generics.DestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    name = 'delete-role'
    lookup_field = "id"

class CreateRole(generics.CreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    name = 'create-role'