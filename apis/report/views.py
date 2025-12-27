from attendance.models import Attendance
from person.models import Person
from capturemethod.models import CaptureMethod
from services.models import Services
from attendance.serializers import attendanceSerializers
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
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from io import BytesIO



#this generic class will handle GET method to be used by the admin alone
class AttendanceList(generics.ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = attendanceSerializers
    permission_classes = [IsAuthenticated,IsInGroup]
    required_groups = requiredGroups(permission='view_attendance')
    name = 'attendance-report'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethodId__id') 

     #you can search using the "search" keyword
    search_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethodId__id')

    #you can order using the "ordering" keyword
    ordering_fields = ('comment','checkInTimestamp','checkOutTimestamp',
                        'personId__id','servicesId__id','captureMethodId__id') 
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(queryset=self.get_queryset()) #still filter
        customQueryset = self.getCustomQueryset(queryset)
        try:
             # 3. Create an Excel workbook
              wb = Workbook()
              ws = wb.active
              ws.title = "Church Attendance"
              # Add headers (using serializer field names or custom names)
              headers =  [
                 'SN','FirstName','LastName', 'Service','CaptureMethod',
                 'CheckInTimestamp','CheckOutTimestamp','Remark',
              ]
              ws.append(headers)
              # Add data rows
              for item in customQueryset:
                   row_values = [item.get(header) for header in headers] # Or customize based on item keys
                   ws.append(row_values)
              #add styles
              self.addStyles(ws)
              self.adjustWidth(ws)
              # 4. Save the workbook to a BytesIO buffer
              excel_buffer = BytesIO()
              wb.save(excel_buffer)
              excel_buffer.seek(0) # Rewind the buffer to the beginning
              # 5. Create an HttpResponse with appropriate headers
              response = HttpResponse(
                 excel_buffer.getvalue(),
                 content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
              )
              response['Content-Disposition'] = 'attachment; filename="church_attendance.xlsx"'
              return response
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def getCustomQueryset(self, queryset):
         data = []
         count = 1
         for obj in queryset:
             capturemethod = CaptureMethod.objects.get(id=obj.captureMethodId.id)
             person = Person.objects.get(pk=obj.personId.id)
             service = Services.objects.get(id=obj.servicesId.id)
             checkout = None
             if obj.checkOutTimestamp is not None:
                checkout = obj.checkOutTimestamp.replace(tzinfo=None)

             newObj = {
                 'SN':count,'FirstName':person.firstName,
                 'LastName':person.lastName, 'Service': service.eventName,
                 'CaptureMethod': capturemethod.method,
                 'CheckInTimestamp': obj.checkInTimestamp.replace(tzinfo=None),
                 'CheckOutTimestamp': checkout,
                 'Remark': obj.comment,
             }
             data.append(newObj)
             count = count + 1
         return data
    def addStyles(self, ws):
        bold_font = Font(bold=True)
        for row in ws.iter_rows():
          for cell in row:
           cell.alignment = Alignment(wrap_text=True)
           # Assign the bold_font object to the cell's font attribute
           cell.font = bold_font
    def adjustWidth(self,ws):
        # Iterate over all columns to adjust their widths
        for col in ws.columns:
          max_length = 0
          column_letter = col[0].column_letter # Get the column letter (e.g., 'A', 'B')
          for cell in col:
            try:
            # Check the length of the cell's value
               if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
            except TypeError: # Handle cases where cell.value might be None
              pass
            # Calculate adjusted width (add a small buffer for visual spacing)
            adjusted_width = (max_length + 2)
            # Set the column width
            ws.column_dimensions[column_letter].width = adjusted_width