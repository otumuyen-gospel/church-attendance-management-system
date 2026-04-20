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
from user.apps import executor

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
        church = Church.objects.get(id=Person.objects.get(id=request.data['personId'])
                                        .churchId.id)
        
        try:
                # Use the executor thread pool to send the email asynchronously
            executor.submit(EmailService.send_welcome_email,
                                request.data['email'],
                               request.data['username'],
                               church.name,
                             role.permissions.split(','),
                             church.logo.url)
        except Exception as e:
                raise Response({"Error": "Failed to send user welcome email"}, status=status.HTTP_400_BAD_REQUEST)
       
        '''
        EmailService.send_welcome_email(
         user_email=request.data['email'],
         user_name=request.data['username'],
         church_name=church.name,
         church_logo=church.logo.url,
         roles = role.permissions.split(',')
        )'''
        
        return Response({"user": serializer.data,
                         "refresh": res["refresh"],
                         "token": res["access"]
                         }, status=status.HTTP_201_CREATED)