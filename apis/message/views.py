from .models import Message
from .serializers import MessageSerializers
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
from .email_service import EmailService
from person.models import Person
from church.models import Church



#this generic class will handle GET method to be used by the admin alone
class MessageList(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_message')
    name = 'message-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('title','detail','recipients','senderId__id','date') 

     #you can search using the "search" keyword
    search_fields = ('title','detail','recipients','senderId__id','date')

    #you can order using the "ordering" keyword
    ordering_fields = ('title','detail','recipients','senderId__id','date')


class DeleteMessage(generics.DestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_message')
    name = 'delete-message'
    lookup_field = "id"

class CreateTextMessage(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_message')
    name = 'create-text-message'

class CreateEmailMessage(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated,IsInGroup]
    required_groups = requiredGroups(permission='add_message')
    name = 'create-email-message'

    def create(self, request, *args, **kwargs):
        person = Person.objects.get(email=request.data['recipients'])
        EmailService.send_generic_email(
            user_email=request.data['recipients'],
            title=request.data['title'],
            detail=request.data['detail'],
            user_name=person.firstName + " " +person.lastName,
            church_name=Church.objects.get(
                id=Person.objects.get(id=self.request.user.personId.id).churchId.id).name
        )
        return super().create(request, *args, **kwargs)