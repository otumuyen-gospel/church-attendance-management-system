from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers.register import SignupSerializer
from django.contrib.auth.models import Group
from user.permissions import IsInGroup
from role.util import requiredGroups
from role.models import Role
from message import EmailService
from church.models import Church
from person.models import Person

class SignupViewset(ViewSet):
    serializer_class = SignupSerializer
    permission_classes = [IsAuthenticated,IsInGroup,]
    required_groups = requiredGroups(permission='add_user')
    http_method_names = ['post']        
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        '''check if user is added to a group otherwise 
        fetch user choosen group and add user to the group
        '''
        role = Role.objects.get(pk=request.data['roleId'])
        group = Group.objects.get(name=role.name)
        user.groups.add(group)

        '''token based authentication instead of 
        direct session, cookie access management
        '''
        refresh = RefreshToken.for_user(user) 
        res = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            }
        
        
        # In your user registration view
        EmailService.send_welcome_email(
         user_email=request.data['email'],
         user_name=request.data['username'],
         church_name=Church.objects.get(id=
                                        Person.objects.get(id=request.data['personId'])
                                        .churchId.id).name,
         roles = role.permissions.split(',')
        )
        
        return Response({"user": serializer.data,
                         "refresh": res["refresh"],
                         "token": res["access"]
                         }, status=status.HTTP_201_CREATED)