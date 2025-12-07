from rest_framework import serializers

class UserPasswordUpdateSerializer(serializers.Serializer):
    #set user password to be 8 char long and can't be read by the user
    password = serializers.CharField(max_length=128,
                                     min_length=8, 
                                     write_only=True, 
                                     required=True)
    
    new_password = serializers.CharField(max_length=128,
                                     min_length=8, 
                                     write_only=True, 
                                     required=True)
   