from django.urls import include, path
from rest_framework.routers import SimpleRouter
from  .viewsets.register import SignupViewset
from .viewsets.login import LoginViewSet
from .viewsets.refresh import RefreshViewSet
from .views import *
from .viewsets.password import UserPasswordUpdateView

router = SimpleRouter()
router.register(r'register', SignupViewset, basename='register')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'refresh', RefreshViewSet, basename='refresh')

urlpatterns = [
    *router.urls,
    path('update-password/<int:id>/', UserPasswordUpdateView.as_view(), name='update-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/request/', PasswordResetRequestAPIView.as_view(), name='request'),
    path('reset/verify/', OTPVerificationAPIView.as_view(), name='verify'),
    path('reset/password/', PasswordResetAPIView.as_view(), name='password'),
    path('logentry/', LogEntryViews.as_view(), name='Log Entries'),

]