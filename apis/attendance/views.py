from django.utils import timezone
from django.db.models import Q

from capturemethod.models import CaptureMethod
from person.models import Person
from services.models import Services

from .models import Attendance
from .serializers import RecognizeFormSerializer, attendanceSerializers
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
class AttendanceList(generics.ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [IsAuthenticated,IsInGroup,]
    required_groups = requiredGroups(permission='view_attendance')
    name = 'attendance-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethodId__id',"attendanceDate") 

     #you can search using the "search" keyword
    search_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethodId__id',"attendanceDate")

    #you can order using the "ordering" keyword
    ordering_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethodId__id',"attendanceDate")


class UpdateAttendance(generics.UpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_attendance')
    name = 'attendance-update'
    lookup_field = "id"

class DeleteAttendance(generics.DestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_attendance')
    name = 'delete-attendance'
    lookup_field = "id"

class CreateAttendance(generics.GenericAPIView):
    serializer_class = RecognizeFormSerializer
    permission_classes = [IsAuthenticated,IsInGroup,]
    required_groups = requiredGroups(permission='add_attendance')

    def capture_attendance(self, personID, servicesId, match=True):
        try:
            person = Person.objects.get(id=personID)
            services = Services.objects.get(id=servicesId)
            capture_method = CaptureMethod.objects.get(method=CaptureMethod.METHOD_FORM)
            
            today = timezone.now().date()
            
            # Check if already attended today
            if Attendance.objects.filter(personId=person, attendanceDate=today, servicesId=services).exists():
                return Response({
                    "message": f"{person.firstName} {person.lastName} has already been marked present for today's {services.eventName}"
                }, status=status.HTTP_200_OK)
            
            # Create attendance record
            Attendance.objects.create(
                personId=person,
                servicesId=services,
                captureMethodId=capture_method,
                remarks = "Attendance captured via form"
            )
            
            return Response({
                "message": f"Attendance successfully captured for {person.firstName} {person.lastName}",
                "person": f"{person.firstName} {person.lastName}",
                "service": services.eventName,
                "date": today,
                "match": match
            }, status=status.HTTP_201_CREATED)
            
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
        except Services.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
        except CaptureMethod.DoesNotExist:
            return Response({"error": "Form capture method not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fullname = serializer.validated_data['fullname']
        services_id = serializer.validated_data['servicesId']
        firstName, _, lastName = fullname.partition(" ")
        try:
            person  = Person.objects.get(Q(firstName=firstName) & Q(lastName=lastName) | 
                                         Q(firstName=lastName) & Q(lastName=firstName))
            # mark attendance
            return self.capture_attendance(personID=person.id, servicesId=services_id, match=True)
        except Person.DoesNotExist:
            return Response({"Match": False, "message": "Person with the provided fullname does not exist"}, status=status.HTTP_404_NOT_FOUND)

