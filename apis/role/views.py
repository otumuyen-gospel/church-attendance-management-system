from .models import Role
from .serializers import RoleSerializers
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
from django.contrib.auth.models import Group, Permission
from .util import requiredGroups


#this generic class will handle GET method to be used by the admin alone
class RoleList(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='view_role')
    name = 'role-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('name','description',)  

     #you can search using the "search" keyword
    search_fields = ('name','description',)   

    #you can order using the "ordering" keyword
    ordering_fields = ('name','description',) 


class UpdateRole(generics.UpdateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='change_role')
    name = 'role-update'
    lookup_field = "id"
    def get_object(self):
        obj = super().get_object()
        grpName = obj.name
        self.updateGroup(name=grpName)
        return obj
    def updateGroup(self, name):
        #delete group if it exist
        Group.objects.get(name=name).delete()
        #recreate group
        newGroupName = self.request.POST.get('name')
        permissions = self.request.POST.get('permissions')
        if permissions is not None:
            newGrp, iscreated = Group.objects.get_or_create(name=newGroupName)
            lists = permissions.split(',')
            if iscreated:
              perms = Permission.objects.filter(codename__in=lists)
              newGrp.permissions.add(*perms)


class DeleteRole(generics.DestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='delete_role')
    name = 'delete-role'
    lookup_field = "id"
    def get_object(self):
        obj = super().get_object()
        grpName = obj.name
        #delete group if it exist
        Group.objects.get(name=grpName).delete()
        return obj

class CreateRole(generics.CreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    permission_classes = [AllowAny,]
    required_groups = requiredGroups(permission='add_role')
    name = 'create-role'
    def create(self, request, *args, **kwargs):
        self.createGroup(request=request)
        return super().create(request, *args, **kwargs)
    def createGroup(self, request):
        name = request.data.get('name')
        permissions = request.data.get('permissions')
        if permissions is not None:
            newGrp, iscreated = Group.objects.get_or_create(name=name)
            lists = permissions.split(',')
            if iscreated:
              perms = Permission.objects.filter(codename__in=lists)
              newGrp.permissions.add(*perms)