from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from ..serializers.login import LoginSerializer
from user.models import User
from church.models import Church
from person.models import Person
from permissions.models import Permissions
from role.models import Role
from django.contrib.auth.models import Permission, Group
from ..serializers.register import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

class LoginViewSet(ViewSet):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']


    def create(self, request, *args, **kwargs):
        self.account_wizard(request)
        serializer =self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data,
                        status=status.HTTP_200_OK)
    '''
    this function helps to create  the admin account on the first time if no admin account exists
    and also login the admin account once created
    '''
    def account_wizard(self, request):
        if not User.objects.exists():  #if no user exists create the admin user
            self.create_permissions()
            self.create_admin_Role()
            church = self.create_admin_church(request)
            person = self.create_admin_person(request, church)
            self.create_admin_user(request, person)
    def create_permissions(self):
        #create the permissions first
            Permissions.objects.all().delete() #clear existing permissions
            all_permissions = Permission.objects.all() # django's permissions
            for perm in all_permissions:
                Permissions.objects.create(
                    permission=perm.codename
                )
    def create_admin_Role(self):
        if not Role.objects.filter(name='admin').exists():
            newGrp, iscreated = Group.objects.get_or_create(name='admin')
            permissions = Permissions.objects.all().values_list('permission', flat=True)
            if iscreated:
                perms = Permission.objects.filter(codename__in=permissions)
                newGrp.permissions.add(*perms)
                admin_role = Role.objects.create(name='admin', description='Administrator role with all permissions',
                                                 permissions=','.join(permissions))
    def create_admin_church(self, request):
        if not Church.objects.filter(name=request.data['username']).exists():
            church = Church.objects.create(
                name=request.data['username'],
                address='Admin Church Address',
                description='Admin Church '
            )
            return church

    def create_admin_person(self, request, church):
        if not Person.objects.filter(firstName=request.data['username']).exists():
            person = Person.objects.create(
                firstName=request.data['username'],
                middleName=request.data['username'],
                lastName=request.data['username'],
                phone='01999999999',
                email=request.data['username'] + "@gmail.com",
                dob='2000-01-01',
                entranceDate=timezone.now(),
                churchId = church.id,

            )
            return person

    def create_admin_user(self, request, person):
        obj = {
            'username':request.data['username'],
            'password':request.data['password'],
            'email':request.data['username'] + "@gmail.com",
            'is_superuser':True,
            'is_staff':True,
            'roleId':Role.objects.get(name='admin').id,
            'is_active':True,
            'personId':person.id,

        }
        serializer = SignupSerializer(data=obj)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        '''check if user is added to a group otherwise 
        fetch user choosen group and add user to the group
        '''
        role = Role.objects.get(name='admin')
        group = Group.objects.get(name=role.name)
        user.groups.add(group)

        '''token based authentication instead of 
        direct session, cookie access management
        '''
        refresh = RefreshToken.for_user(user)
    