from .models import HouseHold
from .serializers import HouseHoldSerializers
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
class HouseHoldList(generics.ListAPIView):
    queryset = HouseHold.objects.all()
    serializer_class = HouseHoldSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_household')
    name = 'household-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('name','address','head','spouse','children','count') 

     #you can search using the "search" keyword
    search_fields = ('name','address','head','spouse','children','count')  

    #you can order using the "ordering" keyword
    ordering_fields = ('name','address','head','spouse','children','count') 


class UpdateHouseHold(generics.UpdateAPIView):
    queryset = HouseHold.objects.all()
    serializer_class = HouseHoldSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_household')
    name = 'household-update'
    lookup_field = "id"

class DeleteHouseHold(generics.DestroyAPIView):
    queryset = HouseHold.objects.all()
    serializer_class = HouseHoldSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_household')
    name = 'delete-household'
    lookup_field = "id"

class CreateHouseHold(generics.CreateAPIView):
    queryset = HouseHold.objects.all()
    serializer_class = HouseHoldSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_household')
    name = 'create-household'