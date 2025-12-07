"""
URL configuration for apis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('church/', include('church.urls'), name='church'),
    path('household/', include('household.urls'), name='Families'),
    path('role/', include('role.urls'), name='Roles'),
    path('permissions/', include('permissions.urls'), name='Permissions'),
    path('capturemethod/', include('capturemethod.urls'), name='Capture Method'),
    path("membership/",include('membership.urls'), name="Membership"),
    path("ministries/",include('ministries.urls'), name="Ministries"),
    path("services/",include('services.urls'), name="Services"),
    path("person/",include('person.urls'), name="Person"),
    path("contact/",include('contact.urls'), name="Contact"),
    path("leadership/",include('leadership.urls'), name="Leadership"),
    path("attendance/",include('attendance.urls'), name="Attendance"),
    path("follow_up_tasks/",include('followup.urls'), name="Follow Up Tasks"),
    path("user_faces/",include('faces.urls'), name="User Faces"),
    path("user/",include('user.urls'), name="Users"),
    path("auth/",include('auth.urls'), name="Auth Pages"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
