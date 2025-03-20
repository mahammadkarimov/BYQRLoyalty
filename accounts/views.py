from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from .serializers import RestaurantCreateSerializer
from base_user.models import Restaurant
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from .serializers import MyTokenObtainPairSerializer


class RestaurantRegisterView(generics.CreateAPIView):
    serializer_class = RestaurantCreateSerializer
    queryset = Restaurant.objects.all()
    permissions = [AllowAny]


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer
   

