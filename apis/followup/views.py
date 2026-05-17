from .models import Followup
from .serializers import FollowupSerializers
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
from django.db.models import Q



#this generic class will handle GET method to be used by the admin alone
class FollowupList(generics.ListAPIView):
    queryset = Followup.objects.all()
    serializer_class = FollowupSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_followup')
    name = 'followup-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('followerId__id','followeeId__id','type',
                        'dueDate','status','comment') 

     #you can search using the "search" keyword
    search_fields =  ('followerId__id','followeeId__id','type',
                        'dueDate','status','comment')  

    #you can order using the "ordering" keyword
    ordering_fields =  ('followerId__id','followeeId__id','type',
                        'dueDate','status','comment') 
    
    def get_queryset(self):
        user = self.request.user
        
        # 1. Admins see every single record in the database
        if user.is_staff and user.is_superuser:
            return self.queryset

        # 2. Regular users only see records where they are the follower or creator
        # Replace 'followerId' and 'creatorId' with your exact model field names (e.g., 'follower' and 'creator')
        return self.queryset.filter(Q(followerId=user) | Q(creatorId=user))


class UpdateFollowup(generics.UpdateAPIView):
    queryset = Followup.objects.all()
    serializer_class = FollowupSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_followup')
    name = 'followup-update'
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        
        # 1. Admins see every single record in the database
        if user.is_staff and user.is_superuser:
            return self.queryset

        # 2. Regular users only see records where they are the follower or creator
        # Replace 'followerId' and 'creatorId' with your exact model field names (e.g., 'follower' and 'creator')
        return self.queryset.filter(Q(followerId=user) | Q(creatorId=user))
    
    def get_object(self):
        """
        Fetches the single object instance securely from the filtered queryset.
        """
        # 1. Searches inside the restricted dataset from get_queryset()
        # 2. Automatically returns a 404 error if someone else's ID is typed in the URL
        obj = super().get_object()
        return obj

class DeleteFollowup(generics.DestroyAPIView):
    queryset = Followup.objects.all()
    serializer_class = FollowupSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_followup')
    name = 'followup-delete'
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        
        # 1. Admins see every single record in the database
        if user.is_staff and user.is_superuser:
            return self.queryset

        # 2. Regular users only see records where they are the follower or creator
        # Replace 'followerId' and 'creatorId' with your exact model field names (e.g., 'follower' and 'creator')
        return self.queryset.filter(creatorId=user)
    
    def get_object(self):
        """
        Fetches the single object instance securely from the filtered queryset.
        """
        # 1. Searches inside the restricted dataset from get_queryset()
        # 2. Automatically returns a 404 error if someone else's ID is typed in the URL
        obj = super().get_object()
        return obj


class CreateFollowup(generics.CreateAPIView):
    queryset = Followup.objects.all()
    serializer_class = FollowupSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_followup')
    name = 'followup-create'

    def perform_create(self, serializer):
      # Set the authenticated user as both creator
      serializer.save(creatorId=self.request.user)



