from django.core.mail import send_mail
from django.utils.timezone import now, timedelta 
from rest_framework import serializers
from user.models import User

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        # Generate OTP and send via email
        user.generate_otp()
        send_mail(
            "Password Reset OTP",
            f"Your OTP for password reset is {user.otp}",
            "portal@school.com",  # Change this to your email
            [user.email],
            fail_silently=False,
        )
        return value



class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        # Check if OTP is correct and not expired
        if user.otp != data["otp"]:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        if user.otp_exp < now():  # OTP expired
            raise serializers.ValidationError({"otp": "OTP expired."})

        # Mark OTP as verified
        user.otp_verified = True
        user.save()

        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        # Check if OTP was verified
        if not user.otp_verified:
            raise serializers.ValidationError({"otp": "OTP verification required."})

        return data

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        user.set_password(self.validated_data["new_password"])
        user.otp = None  # Clear OTP after successful reset
        user.otp_exp = None
        user.otp_verified = False  # Reset verification status
        user.save()
        return user
