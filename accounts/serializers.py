from rest_framework import serializers
from base_user.models import Restaurant
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import get_user_model
User=get_user_model()


class RestaurantCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    class Meta:
        model=Restaurant
        fields=("username","first_name","last_name","email","password", "latitude", "longitude")

    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data, user_type='restaurant')
        user.set_password(user_data['password'])
        user.save()
        restaurant = Restaurant.objects.create(**validated_data, user=user)
        return restaurant
    
    def validate(self, attrs):
        email = attrs.get('email')
        print(email)
        if User.objects.filter(email=email).exists():
            print(User.objects.get(email=email))
            raise serializers.ValidationError('User with this email address already exists')
        return super().validate(attrs)

    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        if user.user_type != 'restaurant':
            raise serializers.ValidationError('No active account found with the given credentials')

        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        return token
    