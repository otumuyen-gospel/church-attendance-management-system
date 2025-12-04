from django.shortcuts import render

# Create your views here.
from .models import FollowUp
from .serializers import FollowUpSerializers
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
class FollowUpList(generics.ListAPIView):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='view_followup')
    name = 'followup-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('followeeId__id','followerId__id','assignment','dueDate','isCompleted') 

     #you can search using the "search" keyword
    search_fields = ('followeeId__id','followerId__id','assignment','dueDate','isCompleted')

    #you can order using the "ordering" keyword
    ordering_fields = ('followeeId__id','followerId__id','assignment','dueDate','isCompleted')


class UpdateFollowUp(generics.UpdateAPIView):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='change_followup')
    name = 'followup-update'
    lookup_field = "id"

class DeleteFollowUp(generics.DestroyAPIView):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='delete_followup')
    name = 'delete-followup'
    lookup_field = "id"

class CreateFollowUp(generics.CreateAPIView):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='add_followup')
    name = 'create-followup'