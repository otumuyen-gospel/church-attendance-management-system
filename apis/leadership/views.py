from .models import Leadership
from .serializers import LeadershipSerializers
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
class LeadershipList(generics.ListAPIView):
    queryset = Leadership.objects.all()
    serializer_class = LeadershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='view_leadership')
    name = 'leadership-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('description',) 

     #you can search using the "search" keyword
    search_fields = ('description',) 

    #you can order using the "ordering" keyword
    ordering_fields = ('description',) 


class UpdateLeadership(generics.UpdateAPIView):
    queryset = Leadership.objects.all()
    serializer_class = LeadershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='change_leadership')
    name = 'leadership-update'
    lookup_field = "id"

class DeleteLeadership(generics.DestroyAPIView):
    queryset = Leadership.objects.all()
    serializer_class = LeadershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='delete_leadership')
    name = 'delete-leadership'
    lookup_field = "id"

class CreateLeadership(generics.CreateAPIView):
    queryset = Leadership.objects.all()
    serializer_class = LeadershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='add_leadership')
    name = 'create-leadership'