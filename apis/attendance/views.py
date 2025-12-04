from .models import Attendance
from .serializers import attendanceSerializers
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
class AttendanceList(generics.ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='view_attendance')
    name = 'attendance-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethod__id') 

     #you can search using the "search" keyword
    search_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethod__id')

    #you can order using the "ordering" keyword
    ordering_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethod__id') 


class UpdateAttendance(generics.UpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='change_attendance')
    name = 'attendance-update'
    lookup_field = "id"

class DeleteAttendance(generics.DestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='delete_attendance')
    name = 'delete-attendance'
    lookup_field = "id"

class CreateAttendance(generics.CreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='add_attendance')
    name = 'create-attendance'