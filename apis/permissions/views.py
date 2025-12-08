from .models import Permissions
from .serializers import PermissionsSerializers
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
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from role.util import requiredGroups
from user.permissions import IsInGroup



#this generic class will handle GET method to be used by the admin alone
class PermissionsList(generics.ListAPIView):
    queryset = Permissions.objects.all()
    serializer_class = PermissionsSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_permissions')
    name = 'permissions-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('permission',)  

     #you can search using the "search" keyword
    search_fields = ('permission',)   

    #you can order using the "ordering" keyword
    ordering_fields = ('permission',) 


class DeleteCreateUpdatePermissions(APIView):
    queryset = Permissions.objects.all()  #my stored permissions
    all_permissions = Permission.objects.all() # django's permissions
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_permissions')
    name = 'update-permissions'
    def post(self,request):
        try:
            if self.clearDb():
              self.populateDb()
            return Response({"success": "operation successful"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def clearDb(self):
        return self.queryset.delete() #empty the database table
    def populateDb(self):
        for perm in self.all_permissions:
            Permissions.objects.create(permission=perm.codename)