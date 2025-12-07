from rest_framework import serializers
from user.serializers import UserSerializers
from user.models import User

class SignupSerializer(UserSerializers):
    #set user password to be 8 char long and can't be read by the user
    password = serializers.CharField(max_length=128,
                                     min_length=8, 
                                     write_only=True, 
                                     required=True)
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ('id','user_permissions','groups','last_login','otp',
                   'otp_exp','otp_verified','is_active','is_superuser','is_staff',
                   'firstname','lastname')
    
    def create(self, validated_data):
        '''call the create_user  method objects instance of 
        User class created from AccountManager class'''
        
        return User.objects.create_user(**validated_data)