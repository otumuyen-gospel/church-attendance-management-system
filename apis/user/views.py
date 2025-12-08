from django.shortcuts import render

# Create your views here.
from .models import User
from role.models import Role
from .serializers import UserSerializers
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
from django.contrib.auth.models import Group
from role.util import requiredGroups
from user.permissions import IsInGroup



#this generic class will handle GET method to be used by the admin alone
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='view_user')
    name = 'user-list'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    #you can filter by field names specified here keyword e.g url?name='church one'
    filterset_fields = ('username','email','personId__id','roleId__id') 

     #you can search using the "search" keyword
    search_fields =  ('username','email','personId__id','roleId__id')  

    #you can order using the "ordering" keyword
    ordering_fields =  ('username','email','personId__id','roleId__id') 


class UpdateUser(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_user')
    name = 'user-update'
    lookup_field = "id"

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_superuser or \
            obj == self.request.user:
             self.updateUserGroup(obj)
             return obj
        else:
            raise PermissionDenied("You do not have permission to edit this object.")
    
    def updateUserGroup(self,obj):
        user = self.queryset.get(pk=obj.id)
        if self.request.data['roleId'] != user.roleId__id: #user changed role so update role
            group = Group.objects.get(name=user.roleId.name)
            role = Role.objects.get(pk=self.request.data['roleId'])
            new_group = Group.objects.get(name=role.name)
            if group in user.groups.all():
              user.groups.remove(group)
              user.groups.add(new_group)

class DeleteUser(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='delete_user')
    name = 'user-delete'
    lookup_field = "id"

class CreateUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='add_user')
    name = 'user-create'