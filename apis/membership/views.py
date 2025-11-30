from .models import Membership
from .serializers import MembershipSerializers
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
from ..role.util import requiredGroups



#this generic class will handle GET method to be used by the admin alone
class MembershipList(generics.ListAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='view_membership')
    name = 'membership-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('status','description',) 

     #you can search using the "search" keyword
    search_fields = ('status','description',) 

    #you can order using the "ordering" keyword
    ordering_fields = ('status','description',) 


class UpdateMembership(generics.UpdateAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='change_membership')
    name = 'membership-update'
    lookup_field = "id"

class DeleteMembership(generics.DestroyAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='delete_membership')
    name = 'delete-membership'
    lookup_field = "id"

class CreateMembership(generics.CreateAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='add_membership')
    name = 'create-membership'