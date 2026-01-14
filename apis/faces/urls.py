"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.urls import path
from .views import *
'''
 Each time a new faces is uploaded or an existing one is updated, admin should 
 remember to cache the face encodings again using the cache management endpoint.
'''
urlpatterns = [
    path('frontend/', FaceFrontendView.as_view(), name='face-frontend'),
    path('views/', FacesList.as_view(), name='faces-list'),
    path('upload/', CreateFaces.as_view(), name='create-faces'),
    path('delete/<int:id>/', DeleteFaces.as_view(), name='delete-faces'),
    path('update/<int:id>/', UpdateFaces.as_view(), name='faces-update'),
    path('recognition/', FaceRecognitionStreamView.as_view(), name='face-recognize'),
    path('cache/', CacheManagementView.as_view(), name='cache-management'),
]
