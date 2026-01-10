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
from .sms_service import SMSService
from person.models import Person
from church.models import Church
from rest_framework.decorators import action
from django.core.exceptions import ImproperlyConfigured



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
    def create(self, request, *args, **kwargs):
        try:
            phone_number = request.data.get('recipients')
            message_title = request.data.get('title')
            message_body = request.data.get('detail')

            if not phone_number or not message_title or not message_body:
                return Response(
                    {'error': 'recipients, title, and detail are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            sms_service = SMSService()
            result = sms_service.send_generic_sms(
                phone_number=phone_number,
                message_title=message_title,
                message_body=message_body
            )

            if result['success']:
                return super().create(request, *args, **kwargs)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = requiredGroups(permission='add_message')
    name = 'send-bulk-sms'
    def create(self, request, *args, **kwargs):
        
        try:
            phone_numbers = request.data.get('recipients')
            message_title = request.data.get('title')
            message_body = request.data.get('detail')

            if not phone_numbers or not isinstance(phone_numbers, list):
                return Response(
                    {'error': 'recipients must be a list and is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not message_title or not message_body:
                return Response(
                    {'error': 'title and detail are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            sms_service = SMSService()
            full_message = f"{message_title}: {message_body}"
            result = sms_service.send_bulk_sms(
                recipient_numbers=phone_numbers,
                message_body=full_message
            )

            if result['success']:
                return super().create(request, *args, **kwargs)

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


