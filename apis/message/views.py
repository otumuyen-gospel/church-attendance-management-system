
from sys import exception

from .models import Message
import re
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
from .sms_service import SMSService
from person.models import Person
from church.models import Church
from rest_framework.decorators import action
from django.core.exceptions import ImproperlyConfigured
from user.apps import executor



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

class SendSMS(generics.CreateAPIView):
    """
    Send SMS message to a single recipient.
    
    Request body:
    {
        "phone_number": "+1234567890",
        "message_title": "Attendance Reminder",
        "message_body": "Please attend the service on Sunday"
    }
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_message')
    name = 'create-text-message'
    def perform_create(self, serializer):
        try:
            phone_number = self.request.data.get('recipients')
            message_title = self.request.data.get('title')
            message_body = self.request.data.get('detail')

            if not phone_number or not message_title or not message_body:
                return Response(
                    {'error': 'recipients(phone number), title, and detail are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            sms = SMSService(
                to_number=phone_number,
                message_title=message_title,
                message_body=message_body,
                type='generic'
            )
            executor.submit(sms.run)

            serializer.save(senderId=self.request.user.personId)
            return super().perform_create(serializer)

        except ImproperlyConfigured as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Error sending SMS: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        

class sendEmailMSG(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='add_message')
    name = 'create-email-message'
    def perform_create(self, serializer):
        recipients = self.request.data.get('recipients')
        title = self.request.data.get('title')
        detail = self.request.data.get('detail')
        if not recipients or not title or not detail:
            return Response({'error': 'Recipients(multiple recipients must be comma-separated without spaces), title, and detail are required'},status=status.HTTP_400_BAD_REQUEST)
        username = []
        recipients_list = recipients.split(',')
        for recipient in recipients_list:
            person = Person.objects.get(email=recipient)
            if person:
                username.append(person.firstName + " " + person.lastName)
        church = Church.objects.get(
                id=Person.objects.get(id=self.request.user.personId.id).churchId.id)
        
        try:
            # Fire and forget: send email in a thread without blocking the main request thread
            executor.submit(EmailService.send_generic_email, recipients.split(','), username, title, detail, church.name, church.logo.url)

            serializer.save(senderId=self.request.user.personId)
        except Exception as e:
            return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        return super().perform_create(serializer)


class SendBulkSMS(generics.CreateAPIView):
    """
    Send SMS to multiple recipients.
    
    Request body:
    {
        "phone_numbers": ["+1234567890", "+0987654321"],
        "message_title": "Service Reminder",
        "message_body": "Sunday service at 10 AM"
    }
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_message')
    name = 'send-bulk-sms'
    def perform_create(self, serializer):
        try:
            phone_numbers = self.request.data.get('recipients').split(',')
            message_title = self.request.data.get('title')
            message_body = self.request.data.get('detail')

            if not phone_numbers or not isinstance(phone_numbers, list):
                return Response(
                    {'error': 'recipients must be a comma-separated string of phone numbers '},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not message_title or not message_body:
                return Response(
                    {'error': 'title and detail are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            full_message = f"{message_title}: {message_body}"
            
            sms = SMSService(
                recipient_numbers=phone_numbers,
                message_body=full_message,
                type='bulk'
            )
            executor.submit(sms.run)

            serializer.save(senderId=self.request.user.personId)
            return super().perform_create(serializer)

        except ImproperlyConfigured as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Error sending bulk SMS: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


