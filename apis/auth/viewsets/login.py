from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from user.serializers import UserSerializers
from message.email_service import EmailService
from ..serializers.login import LoginSerializer
from ..serializers.otp import OTPVerificationSerializer
from user.models import User
from church.models import Church
from person.models import Person
from permissions.models import Permissions
from role.models import Role
from django.contrib.auth.models import Permission, Group
from ..serializers.register import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken, Token
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import serializers
from faces.models import Faces
from faces.apps import FacesConfig
from faces.cache import FacesCache
from datetime import timedelta
from django.utils.timezone import now
from django.core.cache import cache
from user.apps import executor

class PreAuthToken(Token):
    token_type = 'pre_auth'
    lifetime = timedelta(minutes=10)

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['is_2fa_pending'] = True
        return token

class FaceLoginView(ViewSet):
    throttle_scope = 'face_login'
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        
        #recognize user face
        user = self.face_wizard()
        if user:
            if user.two_factor_auth:
               return self.generate_OTP(user)
            else:
                #log user in instead with full access token
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializers(user).data
                },status=status.HTTP_200_OK)
                
        else:
            raise serializers.ValidationError({"Error":"This user credential is invalid"})
        
    def generate_OTP(self, user):
            #Generate Pre-Auth Token
            pre_auth_token = PreAuthToken.for_user(user)

             # Generate OTP and send via email
            user.generate_otp()
    
            #send OTP email/SMS
            ### Send Two-Factor Authentication Email
            church = Church.objects.get(id=(Person.objects.get(id=user.personId.id)
                                        .churchId.id))
            
            try:
                # Use the executor thread pool to send the email asynchronously
                if church.logo:
                    url = church.logo.url
                else:
                    url = None
                executor.submit(EmailService.send_two_factor_email,
                                user.email,
                                user.username,
                                user.otp,
                                url)
            except Exception as e:
                raise Response({"Error": "Failed to send OTP email"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                "detail": "OTP sent",
                "pre_auth_token": str(pre_auth_token)
            })
    
    '''
    this function helps to recognize the user face
    '''
    def face_wizard(self):
        # Load uploaded image
        file = self.request.FILES.get('pics')
        if not file:
            raise serializers.ValidationError({"pics": "No image uploaded"})
        
        # Load uploaded image and get encoding
        unknown_encoding = FacesConfig.face_handler.get_embedding(file.read())
        if not unknown_encoding:
            raise serializers.ValidationError({"Error": "Please upload an image with a face"})

        # Get all known faces from cache
        known_encodings = FacesCache.get_all_encodings()
        known_face_ids = FacesCache.get_face_ids()

        if not known_encodings:
            raise serializers.ValidationError({"Error": "No known faces in database(cache is empty)"})
        
        # Compare faces
        best_index, score = FacesConfig.face_handler.find_best_match(known_encodings, unknown_encoding)
        if best_index is not None and score >= 0.4: # Threshold for a match:
            matched_face_id = known_face_ids[best_index]
            matched_face = Faces.objects.get(id=matched_face_id)
            person = matched_face.personId
            # check if the person has an associated user account
            user = User.objects.filter(personId=person).first()
            if user:
               return user
            else:
                raise serializers.ValidationError({"Error": "face recognized but no user account associated with this face or person"})
        raise serializers.ValidationError({"Error": "Unknown person(face not recognized)"})


class LoginView(ViewSet):
    throttle_scope = 'password_login'
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        if not username or not password:
            return Response({"message":"username and password required"},status=status.HTTP_400_BAD_REQUEST)
        #create first user if no user in the database and make the user the admin
        self.account_wizard(request=request)

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            if user.two_factor_auth:
               return self.generate_OTP(user)
            else:
                #log user in instead with full access token
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializers(user).data
                },status=status.HTTP_200_OK)
                
        else:
            raise serializers.ValidationError({"Error":"This user credential is invalid"})
        
    def generate_OTP(self, user):
            #Generate Pre-Auth Token
            pre_auth_token = PreAuthToken.for_user(user)

             # Generate OTP and send via email
            user.generate_otp()
    
            #send OTP email/SMS
            ### Send Two-Factor Authentication Email
            church = Church.objects.get(id=(Person.objects.get(id=user.personId.id)
                                        .churchId.id))
            
            try:
                # Use the executor thread pool to send the email asynchronously
                if church.logo:
                    url = church.logo.url
                else:
                    url = None
                executor.submit(EmailService.send_two_factor_email,
                                user.email,
                                user.username,
                                user.otp,
                                url)
            except Exception as e:
                raise Response({"Error": "Failed to send OTP email"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                "detail": "OTP sent",
                "pre_auth_token": str(pre_auth_token)
            })
    '''
    this function helps to create  the admin account on the first time if no admin account exists
    and also login the admin account once created
    '''
    def account_wizard(self, request):
        if not User.objects.exists():  #if no user exists create the admin user
            self.create_permissions()
            admin_role = self.create_admin_Role()
            church = self.create_admin_church(request)
            person = self.create_admin_person(request, church)
            self.create_admin_user(request, person, admin_role)
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
            if newGrp:
                perms = Permission.objects.filter(codename__in=permissions)
                newGrp.permissions.add(*perms)
                admin_role = Role.objects.create(name='admin', description='Administrator role with all permissions',
                                                 permissions=','.join(permissions))
                return admin_role
        return Role.objects.filter(name='admin').first()
    def create_admin_church(self, request):
        if not Church.objects.exists():
            church = Church.objects.create(
                name='Assemblies of God Church Alimosho Mega Worship Center',
                address='No 33, Fajumobi, Miccom/Ponle Street, Alimosho Lagos',
                description='Assemblies of God Church Alimosho Mega Worship Center is a vibrant and welcoming church Located in the heart of Alimosho, Lagos.'
            )
            return church
        return Church.objects.first()


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
                churchId = church,

            )
            return person
        return Person.objects.filter(firstName=request.data['username']).first()

    def create_admin_user(self, request, person, role):
        obj = {
            'username':request.data['username'],
            'password':request.data['password'],
            'email':request.data['username'] + "@gmail.com",
            'is_superuser':True,
            'is_staff':True,
            'roleId':role.id,
            'is_active':True,
            'personId':person.id,

        }
        serializer = SignupSerializer(data=obj)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        '''check if user is added to a group otherwise 
        fetch user choosen group and add user to the group
        '''
        group = Group.objects.get(name=role.name)
        user.groups.add(group)

        '''token based authentication instead of 
        direct session, cookie access management
        '''
        refresh = RefreshToken.for_user(user)


class OTPVerificationLoginView(ViewSet):
    throttle_scope = 'otp_login'
    serializer_class = OTPVerificationSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']
    def create(self, request, *args, **kwargs):
        otp_provided = self.request.data.get('otp')
        pre_auth_token_str = self.request.data.get('pre_auth_token')

        if not otp_provided or not pre_auth_token_str:
            return Response({"error":"provide the OTP and pre_auth_token sent to your email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validated_token = PreAuthToken(pre_auth_token_str)
            user_id = validated_token['user_id']
            user = User.objects.get(id=user_id)
            self.verify_OTP(user, otp_provided)
            refresh = RefreshToken.for_user(user)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializers(user).data
                },status=status.HTTP_200_OK)

    def verify_OTP(self, user, otp_provided):
         # Check if OTP is correct and not expired
        if user.otp != otp_provided:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        if user.otp_exp < now():  # OTP expired
            raise serializers.ValidationError({"otp": "OTP expired."})

        # Mark OTP as verified
        user.otp_verified = True
        user.save()
