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
    path('ministries-list/', MinistriesList.as_view(), name='ministries-list'),
    path('new-ministry/', CreateMinistries.as_view(), name='create-ministries'),
    path('remove-ministry/<int:id>/', DeleteMinistries.as_view(), name='delete-ministries'),
    path('modify-ministry/<int:id>/', UpdateMinistries.as_view(), name='ministries-update'),
]
