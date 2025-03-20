from rest_framework import serializers
from django.contrib.auth import get_user_model
from base_user.models import Restaurant, MyUser, LoyaltyCards
import uuid
from django.shortcuts import get_object_or_404
from .models import (
    Waiter,
    Client,
    Interest,
    Hotel,
    RestaurantCampaign,
    RestaurantStory,
    FavoriteRestaurant, EventImages, RestaurantEvent, EventTypes, EventGenres,
    RestaurantCategory, RestaurantSubCategory,
    Museum)
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from meals.serializers import RestaurantPackageSerializer

User = get_user_model()


class GetUserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()
    address = serializers.CharField(source='restaurant.address')

    class Meta:
        model = User
        fields = ("address", "first_name", "profile_photo",)

    def get_profile_photo(self, obj):
        if obj.profile_photo and hasattr(obj.profile_photo, 'url'):

            return f"{obj.profile_photo.url}"
        else:
            return None


class GetUpdateSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source='restaurant.address')
    category = serializers.CharField(source='restaurant.category')

    class Meta:
        model = User
        fields = (
            "address",
            "first_name",
            "profile_photo",
            "category",
        )

    def update(self, instance, validated_data):
        # Handle the update of the address if it's provided in the validated_data
        restaurant_data = validated_data.pop('restaurant', {})
        address = restaurant_data.get('address', None)
        category = restaurant_data.get('category', None)
        if address is not None:
            instance.restaurant.address = address
            instance.restaurant.save()

        if category is not None:
            instance.restaurant.category = category
            instance.restaurant.save()

        # Update other fields of the User model
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WaiterRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Waiter
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
        )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data, user_type='waiter')
        user.set_password(user_data["password"])
        user.save()
        restaurant = validated_data.pop('restaurant')
        waiter = Waiter.objects.create(**validated_data, user=user, restaurant=restaurant)
        return waiter

    def validate(self, attrs):
        user_data = attrs.get('user')
        email = user_data.get('email')
        print(email)
        if User.objects.filter(email=email).exists():
            print(1, User.objects.filter(email=email))
            raise serializers.ValidationError('User with this email address already exists')
        return super().validate(attrs)


class WaiterLoginSerializer(serializers.ModelSerializer):
    waiter_id = serializers.CharField(source='waiter.waiter_id')

    class Meta:
        model = User
        fields = (
            'waiter_id',
            'password',
        )

    def validate(self, attrs):
        waiter_id = attrs.get('waiter_id')
        waiter = get_object_or_404(Waiter, waiter_id=waiter_id)
        user = waiter.user
        password = attrs.get('password')
        if not user.exists():
            raise serializers.ValidationError({"error": "not found user"})
        elif user[0].user_type != 'waiter':
            raise serializers.ValidationError({"error": "not found user"})
        user = user.get()
        print(user.user_type)
        if not user.check_password(password):
            raise serializers.ValidationError({"error": "wrong password"})

        return attrs

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        notification_token = user.waiter.notification_token
        return {
            'refresh': str(refresh),
            'access': str(access),
            'notification': notification_token
        }

    def to_representation(self, instance):
        tokens = self.get_tokens(instance)
        return tokens


class WaiterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'profile_photo',
        )


class WaiterProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'profile_photo',
        )


class WaiterNotifySerializer(serializers.Serializer):
    table_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)
    body = serializers.CharField(max_length=1000)


class WaiterPasswordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'password',
        )

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        instance.set_password(password)
        instance.save()
        return super().update(instance, validated_data)


class WaiterNotificatioTokenUpdateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Waiter
        fields = (
            'notification_token',
        )


class WaiterGetSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    restaurant = serializers.SerializerMethodField()
    profile_photo = serializers.ImageField(source='user.profile_photo')
    restaurant_first_name = serializers.CharField(source='restaurant.user.first_name')
    restaurant_last_name = serializers.CharField(source='restaurant.user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    display_card = serializers.BooleanField(source='restaurant.show_tip_card')

    class Meta:
        model = Waiter
        fields = (
            'id',
            'waiter_id',
            'first_name',
            'last_name',
            'balance',
            'email',
            'username',
            'profile_photo',
            'restaurant',
            'restaurant_first_name',
            'restaurant_last_name',
            'display_card',
            'card_name',
            'card_mask',
            'slug'
        )

    def get_restaurant(self, obj):
        if obj.restaurant:
            return obj.restaurant.user.username
        return None


class ClientRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = (
            'full_name',
            'email',
            'password'
        )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        full_name = validated_data.pop('full_name')
        full_name = full_name.split()
        first_name = full_name.pop(0)
        last_name = ' '.join(full_name)
        user = User.objects.create(**user_data, user_type='client', first_name=first_name, last_name=last_name,
                                   username=(''.join(full_name) + uuid.uuid4().hex[:6].upper()))
        user.set_password(user_data["password"])
        user.save()
        client = Client.objects.create(user=user)
        return client

    # def validate(self, attrs):
    #     email = attrs.get('email')
    #     if User.objects.filter(email=email).exists:
    #         raise serializers.ValidationError('User with this email address already exists')
    #     return super().validate(attrs)


class ClientLoyalRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = (
            'full_name',
            'email',
            'password'
        )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        full_name = validated_data.pop('full_name')
        full_name = full_name.split()
        first_name = full_name.pop(0)
        last_name = ' '.join(full_name)
        user = User.objects.create(**user_data, user_type='client', is_loyal=True, first_name=first_name,
                                   last_name=last_name,
                                   username=(''.join(full_name) + uuid.uuid4().hex[:6].upper()))
        user.set_password(user_data["password"])
        user.save()
        client = Client.objects.create(user=user)
        return client


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = (
            'id',
            'title',
            'icon'
        )


class ClientGetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    phone_number = serializers.CharField(source='user.phone_number')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    profile_photo = serializers.ImageField(source='user.profile_photo')
    interests = InterestSerializer(read_only=True, many=True)

    class Meta:
        model = Client
        fields = (
            'id',
            'email',
            'username',
            'phone_number',
            'first_name',
            'last_name',
            'profile_photo',
            'interests',
            'slug'
        )


class HotelRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username')
    profile_photo = serializers.ImageField(source='user.profile_photo')

    class Meta:
        model = Hotel
        fields = (
            'first_name',
            'last_name',
            'username',
            'profile_photo',
            'email',
            'password'
        )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data, user_type='hotel')
        user.set_password(user_data["password"])
        user.save()
        hotel = Hotel.objects.create(user=user)
        return hotel

    def validate(self, attrs):
        email = attrs.get('email')
        print('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User with this email address already exists')
        return super().validate(attrs)


class HotelLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )

    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.filter(email=email)
        password = attrs.get('password')
        if not user.exists():
            raise serializers.ValidationError({"error": "not found user"})
        elif user[0].user_type != 'hotel' and user[0].user_type != 'restaurant':
            raise serializers.ValidationError({"error": "not found user"})
        user = user.get()
        print(user.user_type)
        if not user.check_password(password):
            raise serializers.ValidationError({"error": "wrong password"})

        return attrs

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        profile_photo = user.profile_photo.url
        user_type = user.user_type

        if user_type == 'restaurant':
            package = RestaurantPackageSerializer(user.restaurant.package).data
            return {
                'refresh': str(refresh),
                'access': str(access),
                'username': str(username),
                'first_name': str(first_name),
                'last_name': str(last_name),
                'profile_photo': str(profile_photo),
                'user_type': str(user_type),
                'package': package,
                # 'loyalty_discount_percent': loyalty_discount_percent,

            }
        return {
            'refresh': str(refresh),
            'access': str(access),
            'username': str(username),
            'first_name': str(first_name),
            'last_name': str(last_name),
            'profile_photo': str(profile_photo),
            'user_type': str(user_type)
        }

    def to_representation(self, instance):
        tokens = self.get_tokens(instance)
        return tokens


class RestaurantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    profile_photo = serializers.ImageField(source='user.profile_photo')

    class Meta:
        model = Restaurant
        fields = (
            'id',
            'username',
            'restaurant_name',
            'profile_photo',
            'average_rating',
            'description',
            'loyalty_discount_percent',
            'has_technical_service'
        )


class RestaurantFbpixelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'fbpixel',
        )


class HotelGetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    profile_photo = serializers.ImageField(source='user.profile_photo')
    user_type = serializers.CharField(source='user.user_type')
    restaurants = RestaurantSerializer(many=True)

    class Meta:
        model = Hotel
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'profile_photo',
            'address',
            'user_type',
            'restaurants',
            'slug'
        )


class HotelAdminGetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    profile_photo = serializers.ImageField(source='user.profile_photo')

    class Meta:
        model = Hotel
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'address',
            'profile_photo',
            'slug'
        )


class ClientLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )

    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.filter(email=email)
        password = attrs.get('password')
        if not user.exists():
            raise serializers.ValidationError({"error": "not found user"})
        elif user[0].user_type != 'client':
            raise serializers.ValidationError({"error": "not found user"})
        user = user.get()
        print(user.user_type)
        if not user.check_password(password):
            raise serializers.ValidationError({"error": "wrong password"})
        return attrs

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        client_data = {}
        if user.is_loyal and hasattr(user, 'client'):
            client_data = {
                'barcode_image': user.client.barcode_image.url if user.client.barcode_image else None,
                'card_id': user.client.card_id,
            }

        return {
            'refresh': str(refresh),
            'access': str(access),
            'profile_photo': str(user.profile_photo) if user.profile_photo else None,
            'full_name': f'{user.first_name} {user.last_name}',
            'email': str(user.email),
            'is_loyal': user.is_loyal,
            **client_data,
        }

    def to_representation(self, instance):
        tokens = self.get_tokens(instance)
        return tokens

    def to_representation(self, instance):
        tokens = self.get_tokens(instance)
        return tokens


class HotelUpdateSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(source='user.profile_photo')

    class Meta:
        model = Hotel
        fields = (
            'address',
            'profile_photo'
        )

    def update(self, instance, validated_data):
        profile_photo_data = validated_data.pop('user', {}).get('profile_photo', None)
        if profile_photo_data is not None:
            instance.user.profile_photo = profile_photo_data
        # Update other fields of the Hotel model
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'user_type',
        )


class RestaurantUserTypeSerializer(serializers.ModelSerializer):
    package = RestaurantPackageSerializer(source='restaurant.package')

    class Meta:
        model = User
        fields = (
            'user_type',
            'package'
        )


class RestaurantCampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCampaign
        fields = (
            'name',
            'cover',
        )

    def validate(self, attrs):
        restaurant = self.context.get('request').user.restaurant
        attrs['restaurant'] = restaurant
        return super().validate(attrs)


class RestaurantCampaignGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCampaign
        fields = (
            'id',
            'name',
            'cover',
            'created_at',
            'updated_at'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }


class RestaurantStoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantStory
        fields = (
            'id',
            'cover',
            'created_at',
        )


class RestaurantWithStorySerializer(serializers.ModelSerializer):
    stories = RestaurantStoryGetSerializer(many=True)
    name = serializers.SerializerMethodField()
    profile_photo = serializers.ImageField(source='user.profile_photo')

    class Meta:
        model = Restaurant
        fields = (
            'name',
            'profile_photo',
            'stories',

        )

    def get_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name


class RestaurantStroryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantStory
        fields = (
            'cover',
        )

    def validate(self, attrs):
        restaurant = self.context.get('request').user.restaurant
        attrs['restaurant'] = restaurant
        return super().validate(attrs)


class RestaurantStoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantStory
        fields = (
            'cover',
            'is_activate'
        )

    def validate(self, attrs):
        restaurant = self.context.get('request').user.restaurant
        attrs['restaurant'] = restaurant
        return super().validate(attrs)


class RestaurantListSerialzier(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    profile_photo = serializers.ImageField(source='user.profile_photo')
    name = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = (
            'id',
            'username',
            'name',
            'description',
            'profile_photo',
            'average_rating',
            'review_count',
            'slug',
            'loyalty_discount_percent'
        )

    def get_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name


class ClientUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    birthday = serializers.DateField(write_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'full_name',
            'profile_photo',
            'profile_photo_url',
            'phone_number',
            'email',
            'birthday'
        )

    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            return f"{settings.CDN_BASE_URL}/{obj.profile_photo}"
        return f"{settings.CDN_BASE_URL}/default.png"

    def update(self, instance, validated_data):
        try:
            full_name = validated_data.pop('full_name')
            full_name = full_name.split()
            first_name = full_name.pop(0)
            last_name = ' '.join(full_name)
            birthday = validated_data.pop('birthday')
        except:
            first_name = instance.first_name
            last_name = instance.last_name
            birthday = instance.client.birthday
        instance.client.birthday = birthday
        instance.client.save()
        instance.first_name = first_name
        instance.last_name = last_name
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Return the response in the same format as `ClientSerializer`."""
        return {
            "user_full_name": instance.get_full_name(),
            "email": instance.email,
            "profile_image": self.get_profile_photo_url(instance),
            "gender": instance.gender if hasattr(instance, 'gender') else None,
            "phone_number": instance.phone_number,
        }


class ClientPasswordUpdateSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'password',
            'new_password',
        )

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        password = validated_data.get('password')
        if user.check_password(password):
            new_password = validated_data.get('new_password')
            instance.set_password(new_password)
            instance.save()
            return instance
        raise serializers.ValidationError('Wrong password!')


class FavoriteRestaurantListSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = FavoriteRestaurant
        fields = (
            'id',
            'restaurant',
            'created_at'
        )


class FavoriteRestaurantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRestaurant
        fields = (
            'id',
            'restaurant',
            'created_at'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True}
        }

    def validate(self, attrs):
        client = self.context['request'].user.client
        attrs['client'] = client
        return super().validate(attrs)


from rest_framework import serializers
from .models import RestaurantEvent, EventImages


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImages
        fields = ['image']


class RestaurantEventSerializer(serializers.ModelSerializer):
    images = EventImageSerializer(many=True, read_only=True)  # Display existing images
    image_files = serializers.ListField(  # For uploading multiple images
        child=serializers.ImageField(write_only=True), required=False
    )

    class Meta:
        model = RestaurantEvent
        fields = [
            'id', 'name', 'age', 'genre', 'music_type', 'entry_information',
            'description', 'phone', 'address', 'map_url', 'images', 'image_files',
            'start_date',
        ]

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        event = RestaurantEvent.objects.create(**validated_data)

        for image in image_files:
            EventImages.objects.create(event=event, image=image)

        return event

    def update(self, instance, validated_data):
        # Delete existing images if new images are being uploaded
        image_files = validated_data.pop('image_files', [])
        if image_files:
            # Delete all previous images for this event
            instance.images.all().delete()

        # Update other fields in instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Add new images if provided
        for image in image_files:
            EventImages.objects.create(event=instance, image=image)

        return instance


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTypes
        fields = "__all__"


class EventGenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGenres
        fields = "__all__"


class RestaurantCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCategory
        fields = "__all__"


class RestaurantSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantSubCategory
        fields = "__all__"


class MuseumRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)

    class Meta:
        model = Museum
        fields = (
            "email",
            "password",
            "name",
            "background_image",
        )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        name = validated_data.pop('name')
        background_image = validated_data.pop('background_image')
        first_name = name
        last_name = name
        full_name = first_name + last_name
        user = User.objects.create(**user_data, user_type='museum', first_name=first_name, last_name=last_name,
                                   username=(''.join(full_name) + uuid.uuid4().hex[:6].upper()))
        user.set_password(user_data["password"])
        user.save()
        museum = Museum.objects.create(user=user,
                                       name=name,
                                       background_image=background_image)
        return museum


class ClientSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    profile_image = serializers.SerializerMethodField()
    gender = serializers.CharField(source="user.gender", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Client
        fields = '__all__'

    def get_profile_image(self, obj):
        if obj.user.profile_photo:
            return f"{settings.CDN_BASE_URL}/{obj.user.profile_photo}"
        return f"{settings.CDN_BASE_URL}/default.png"


class FCMTokenUpdateSerializer(serializers.ModelSerializer):
    fcm_token = serializers.CharField(required=True, max_length=500)

    class Meta:
        model = MyUser
        fields = ['fcm_token']


"""
Loyalty part will be replaced to main codes part
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import LoyalUser, MyUser
from django.core.mail import send_mail



class LoyalUserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = LoyalUser
        fields = ['email', 'password', 'first_name', 'last_name', 'father_name', 'birthday_date', 'phone', 'address']

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')

        user = MyUser.objects.create_user(
            email=email,
            password=password,
            is_loyal=True,
            username=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False
        )

        loyal_user = LoyalUser.objects.create(user=user, **validated_data)
        loyal_user.generate_otp()

        send_mail(
            'OTP Kodunuz',
            f'Sizin OTP kodunuz: {loyal_user.one_time_otp}',
            'byqraz@gmail.com',
            [email],
            fail_silently=False,
        )

        return loyal_user



class LoyalUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Email və ya şifrə yanlışdır.")

        if not user.is_active:
            raise serializers.ValidationError("Bu hesab deaktiv edilib.")

        try:
            loyal_user = user.loyal_users  # Get the LoyalUser profile
        except LoyalUser.DoesNotExist:
            raise serializers.ValidationError("Bu istifadəçi loyal user deyil.")

        refresh = RefreshToken.for_user(user)

        return {
            "user": loyal_user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, write_only=True)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp_code')

        try:
            user = MyUser.objects.get(email=email)
            loyal_user = user.loyal_users
            print("Loyal user", loyal_user)
        except (MyUser.DoesNotExist, LoyalUser.DoesNotExist):
            raise serializers.ValidationError("Bu email ilə istifadəçi tapılmadı.")

        if loyal_user.one_time_otp != otp_code:
            raise serializers.ValidationError("OTP kod yanlışdır.")

        # OTP doğrudursa, user-i aktiv edirik
        user.is_active = True
        user.save()
        loyal_user.one_time_otp = None  # OTP-ni silirik
        loyal_user.save()

        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": loyal_user.id,
                "name": loyal_user.first_name,  # Adı varsa əlavə et
                "email": user.email,  # İstifadəçi email-i
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class LoyalCardCreateSerializer(serializers.ModelSerializer):
    restaurant_username = serializers.CharField(write_only=True)

    class Meta:
        model = LoyaltyCards
        fields = ["restaurant_username", "card_id", "image"]
        read_only_fields = ["card_id", "image"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user  # İstifadəçi request-dən alınır

        # Kullanıcının LoyalUser olduğunu yoxla
        try:
            loyal_user = user.loyal_users
        except LoyalUser.DoesNotExist:
            raise serializers.ValidationError("LoyalUser məlumatı tapılmadı.")

        # Restoranı tap
        restaurant_username = validated_data.get("restaurant_username")
        try:
            restaurant = Restaurant.objects.get(user__username=restaurant_username)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Restoran tapılmadı.")

        # Loyal kartı yarat
        loyalty_card = LoyaltyCards.objects.create(
            client=loyal_user,
            restaurant=restaurant
        )

        return loyalty_card