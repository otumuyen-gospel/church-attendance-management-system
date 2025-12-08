from .models import Person
from .serializers import PersonSerializers
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
class PersonList(generics.ListAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_person')
    name = 'person-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('churchId__id','householdId__id','membershipId__id',
                        'firstName','lastName','middleName','dob','phone',
                        'email','entranceDate') 

     #you can search using the "search" keyword
    search_fields =  ('churchId__id','householdId__id','membershipId__id',
                        'firstName','lastName','middleName','dob','phone',
                        'email','entranceDate')  

    #you can order using the "ordering" keyword
    ordering_fields =  ('churchId__id','householdId__id','membershipId__id',
                        'firstName','lastName','middleName','dob','phone',
                        'email','entranceDate') 


class UpdatePerson(generics.UpdateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_person')
    name = 'person-update'
    lookup_field = "id"

class DeletePerson(generics.DestroyAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_person')
    name = 'person-delete'
    lookup_field = "id"

class CreatePerson(generics.CreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_person')
    name = 'person-create'