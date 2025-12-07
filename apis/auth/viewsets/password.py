from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import status
from ..serializers.password import UserPasswordUpdateSerializer
from django.contrib.auth.models import Group
from user.permissions import IsInGroup
from user.models import User
from role.util import requiredGroups

class UserPasswordUpdateView(GenericAPIView):
    serializer_class = UserPasswordUpdateSerializer
    
    permission_classes = [IsAuthenticated, IsInGroup,]
    required_groups = requiredGroups(permission='change_user')
    http_method_names = ['put']      

    def put(self, request, id):
        user = User.objects.get(pk=id)
        if self.request.user.is_superuser or \
        user == self.request.user:
           password = request.data['password'];
           new_password = request.data['new_password']
           if not user.check_password(raw_password=password):
              return Response({"detail": "user password does not match existing",}, 
                        status=status.HTTP_400_BAD_REQUEST)
           else:
             user.set_password(new_password)
             user.save()
             return Response({"detail": "password changed successfully",}, 
                        status=status.HTTP_201_CREATED)
        else:
           return Response({"detail": "You are not permitted carry out this operation",}, 
                        status=status.HTTP_401_UNAUTHORIZED)