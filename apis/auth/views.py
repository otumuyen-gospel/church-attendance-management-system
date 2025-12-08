from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers.otp import (PasswordResetRequestSerializer, 
                              OTPVerificationSerializer, 
                              PasswordResetSerializer)
from .serializers.logentry import LogEntrySerializer
from rest_framework import generics
from auditlog.models import LogEntry
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from user.permissions import IsInGroup


'''
after blacklisting a token or loging out remember to delete
any storage of tokens details in frontend or browser local
storage to avoid using it again 
'''
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)



class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny,]
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "message": "OTP sent to email."}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    

class OTPVerificationAPIView(APIView):
    permission_classes = [AllowAny,]
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"success": True, "message": "OTP verified successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny,]
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
class LogEntryViews(generics.ListAPIView):
    queryset = LogEntry.objects.all().order_by('-timestamp')
    serializer_class = LogEntrySerializer
    permission_classes = [AllowAny,]
    #required_groups = ['admin',]
    name = 'user-logs'