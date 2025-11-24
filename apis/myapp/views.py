from django.shortcuts import render
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework import generics
from rest_framework.response import Response
from .models import Myapp 
from .serializers import MyappSerializers
 
class MyappView(generics.ListCreateAPIView):
    queryset = Myapp.objects.all()
    serializer_class = MyappSerializers
    name = 'myapp'
