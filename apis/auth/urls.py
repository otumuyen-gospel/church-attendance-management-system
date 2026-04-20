from django.urls import include, path
from rest_framework.routers import SimpleRouter
from  .viewsets.register import SignupViewset
from .viewsets.login import FaceLoginView, LoginView, OTPVerificationLoginView
from .viewsets.refresh import RefreshViewSet
from .views import *
from .viewsets.password import UserPasswordUpdateView

router = SimpleRouter()
#router.register(r'register', SignupViewset, basename='register')
router.register(r'refresh', RefreshViewSet, basename='refresh')
#router.register(r'face-login', FaceLoginView, basename='face-login')
#router.register(r'login', LoginView, basename='login')
router.register(r'verify-login', OTPVerificationLoginView, basename='otp-verification-login')

urlpatterns = [
    *router.urls,
    path('user-password-update/<int:id>/', UserPasswordUpdateView.as_view(), name='update-password'),
    path('logout-user/', LogoutView.as_view(), name='logout'),
    #path('email-verification/', PasswordResetRequestAPIView.as_view(), name='request'),
    path('otp-verification/', OTPVerificationAPIView.as_view(), name='verify'),
    path('password-reset/', PasswordResetAPIView.as_view(), name='password'),
    path('user-log-entries/', LogEntryViews.as_view(), name='Log Entries'),

]