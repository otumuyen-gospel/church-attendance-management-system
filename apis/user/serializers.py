from rest_framework import serializers
from .models import User

class UserSerializers(serializers.ModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
       # fields = '__all__'
        exclude = ('id','user_permissions','groups','last_login','otp',
                   'otp_exp','otp_verified','is_active','is_superuser','is_staff',)
        


class UserUpdateSerializers(serializers.ModelSerializer):
    pk = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
       # fields = '__all__'
        exclude = ('id','user_permissions','groups','last_login','otp',
                   'otp_exp','otp_verified','is_active','is_superuser','is_staff',)
        
    def update(self, instance, validated_data):
        password = validated_data.pop('password',None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
            instance.save()
        return instance