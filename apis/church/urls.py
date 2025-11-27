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
urlpatterns = [
    path('views/', ChurchList.as_view(), name=ChurchList.name),
    path('create/', CreateChurch.as_view(), name=CreateChurch.name),
    path('delete/<int:id>/', DeleteChurch.as_view(), name=DeleteChurch.name),
    path('update/<int:id>/', UpdateChurch.as_view(), name=UpdateChurch.name),
]
