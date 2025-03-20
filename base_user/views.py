from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import EventImages, RestaurantEvent, EventGenres, EventTypes, LoyaltyCards
from .serializers import RestaurantEventSerializer, OTPVerificationSerializer, LoyalCardCreateSerializer
from .serializers import EventTypeSerializer, EventGenresSerializer
from django.db.models import Q
import requests, jwt
import json
from .apple import generate_apple_client_secret
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from django.shortcuts import get_object_or_404, get_list_or_404
from .models import (Waiter, Client, Restaurant,
                     RestaurantCampaign, RestaurantStory, FavoriteRestaurant,
                     RestaurantCategory, RestaurantSubCategory, Museum)
from base_user.models import Hotel
from django.utils.translation import activate
from meals.serializers import RestaurantPackageSerializer
from django_filters.rest_framework.backends import DjangoFilterBackend
from .serializers import (
    GetUserSerializer,
    GetUpdateSerializer,
    WaiterLoginSerializer,
    WaiterRegisterSerializer,
    WaiterGetSerializer,
    WaiterUpdateSerializer,
    WaiterProfileUpdateSerializer,
    WaiterPasswordUpdateSerializer,
    WaiterNotificatioTokenUpdateSerialzier,
    WaiterNotifySerializer,
    ClientRegisterSerializer,
    ClientGetSerializer,
    ClientLoginSerializer,
    HotelLoginSerializer,
    HotelRegisterSerializer,
    HotelGetSerializer,
    HotelUpdateSerializer,
    HotelAdminGetSerializer,
    UserTypeSerializer,
    RestaurantUserTypeSerializer,
    RestaurantCampaignGetSerializer,
    RestaurantCampaignCreateSerializer,
    RestaurantListSerialzier,
    RestaurantStoryGetSerializer,
    RestaurantStroryCreateSerializer,
    RestaurantStoryUpdateSerializer,
    RestaurantWithStorySerializer,
    ClientUpdateSerializer,
    ClientPasswordUpdateSerializer,
    FavoriteRestaurantCreateSerializer,
    FavoriteRestaurantListSerializer,
    RestaurantFbpixelSerializer,
    RestaurantSubCategorySerializer,
    RestaurantCategorySerializer,
    MuseumRegisterSerializer,
    ClientLoyalRegisterSerializer, ClientSerializer,
    FCMTokenUpdateSerializer

)
from .filter import RestaurantSubCategoryFilter
from restaurants.models import Table
from rest_framework import generics
from .firebase.notification import send_notification
from django.contrib.auth import get_user_model, authenticate
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Exists, OuterRef
from drf_spectacular.utils import extend_schema

User = get_user_model()


class MuseumRegisterView(generics.CreateAPIView):
    queryset = Museum.objects.all()
    serializer_class = MuseumRegisterSerializer


class UserGetApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        serializer = GetUserSerializer(request.user)
        return Response(serializer.data)


class UpdateUserApi(generics.UpdateAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)
    serializer_class = GetUpdateSerializer

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class WaiterRegisterView(generics.CreateAPIView):
    serializer_class = WaiterRegisterSerializer
    queryset = Waiter.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)


@api_view(['POST'])
def waiter_login_view(request):
    waiter_id = request.data.get('waiter_id')
    password = request.data.get('password')
    waiter = get_object_or_404(Waiter, waiter_id=waiter_id)
    email = waiter.user.email
    print(waiter_id, email, password)
    user = authenticate(email=email, password=password)
    print(user)
    if user:
        if user.user_type == 'waiter':
            serializer = WaiterLoginSerializer(instance=user)
            return Response(serializer.data)
    return Response({'detail': 'ID or Password is wrong!'}, status=status.HTTP_400_BAD_REQUEST)


class WaiterRetrieveView(generics.RetrieveAPIView):
    queryset = Waiter.objects.all()
    serializer_class = WaiterGetSerializer

    def get_object(self):
        username = self.kwargs.get('username')
        waiter = get_object_or_404(Waiter, user__username=username)
        return waiter


class WaiterListView(generics.ListAPIView):
    queryset = Waiter.objects.all()
    serializer_class = WaiterGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.restaurant
        queryset = get_list_or_404(Waiter, restaurant=restaurant)
        return queryset


class WaiterProfileView(generics.RetrieveAPIView):
    queryset = Waiter.objects.all()
    serializer_class = WaiterGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        waiter = get_object_or_404(Waiter, user=user)
        return waiter


class WaiterNotifyView(APIView):
    @swagger_auto_schema(
        request_body=WaiterNotifySerializer,
        responses={
            200: 'Notification sent successfully',
            400: 'Bad request',
            404: 'Waiter not found'
        }
    )
    def post(self, request, *args, **kwargs):
        table_id = request.data.get('table_id')
        title = request.data.get('title')
        body = request.data.get('body')

        table = get_object_or_404(Table, table_id=table_id)
        waiter_id = table.current_waiter.id

        if not waiter_id or not title or not body:
            return Response({"error": "waiter_id, title, and body are required fields."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            waiter = Waiter.objects.get(id=waiter_id)
            send_notification(waiter.notification_token, title, body)
            return Response({"message": "Notification sent successfully"}, status=status.HTTP_200_OK)
        except Waiter.DoesNotExist:
            return Response({"error": "Waiter not found"}, status=status.HTTP_404_NOT_FOUND)


class ClientRegisterView(generics.CreateAPIView):
    serializer_class = ClientRegisterSerializer
    queryset = User.objects.all()


class ClientLoyalRegisterView(generics.CreateAPIView):
    serializer_class = ClientLoyalRegisterSerializer
    queryset = User.objects.all()


class ClientLoginView(APIView):
    @swagger_auto_schema(
        request_body=ClientLoginSerializer,
        responses={
            200: 'Login successful',
            400: 'Bad request'}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        print(email, password)
        user = authenticate(email=email, password=password)
        print(user)
        if user:
            serializer = ClientLoginSerializer(instance=user)
            return Response(serializer.data)
        return Response({'detail': 'Email or Password is wrong!'}, status=status.HTTP_400_BAD_REQUEST)


class ClientListView(generics.ListAPIView):
    serializer_class = ClientGetSerializer
    queryset = Client.objects.all()


class ClientRetrieveView(generics.RetrieveAPIView):
    serializer_class = ClientGetSerializer
    queryset = Client.objects.all()

    def get_object(self):
        slug = self.kwargs.get('slug')
        client = get_object_or_404(Client, slug=slug)
        return client


class HotelRegisterView(generics.CreateAPIView):
    serializer_class = HotelRegisterSerializer
    queryset = User.objects.all()


@api_view(['POST'])
def hotel_login_view(request):
    if request.content_type != 'application/json':
        return Response({'detail': 'Invalid Content-Type. Expected application/json.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Access email and password from request.data (DRF should parse it automatically)
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'detail': 'Email or password is missing.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate the user    
    user = authenticate(email=email, password=password)
    print(user)
    if user:
        if user.user_type in ['hotel', 'restaurant', 'museum']:
            serializer = HotelLoginSerializer(instance=user)
            return Response(serializer.data)
    return Response({'detail': 'Email or Password is wrong!'}, status=status.HTTP_400_BAD_REQUEST)


class HotelRetrieveView(generics.RetrieveAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelGetSerializer

    def get_object(self):
        username = self.kwargs.get('username')
        hotel = get_object_or_404(Hotel, user__username=username)
        return hotel


class HotelListView(generics.ListAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelGetSerializer
    permission_classes = [AllowAny]


class HotelUpdateView(generics.UpdateAPIView):
    serializer_class = HotelUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user.hotel


class HotelAdminGetView(generics.RetrieveAPIView):
    serializer_class = HotelAdminGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user.hotel


class HotelWaiterRegisterAdminView(generics.CreateAPIView):
    serializer_class = WaiterRegisterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        username = self.kwargs.get('restaurant_username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        serializer.save(restaurant=restaurant)


class HotelWaiterListAdminView(generics.ListAPIView):
    serializer_class = WaiterGetSerializer
    queryset = Waiter.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get('restaurant_username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        queryset = restaurant.waiters.all()
        return queryset


class WaiterUpdateView(generics.UpdateAPIView):
    serializer_class = WaiterUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('waiter_slug')
        waiter = get_object_or_404(Waiter, slug=slug)
        return waiter.user


class WaiterProfileUpdateView(generics.UpdateAPIView):
    serializer_class = WaiterProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user


class WaiterPasswordUpdateView(generics.UpdateAPIView):
    serializer_class = WaiterPasswordUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('waiter_slug')
        waiter = get_object_or_404(Waiter, slug=slug)
        return waiter.user


class WaiterDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('waiter_slug')
        waiter = get_object_or_404(Waiter, slug=slug)
        return waiter.user


class WaiterGetView(generics.RetrieveAPIView):
    serializer_class = WaiterGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('waiter_slug')
        waiter = get_object_or_404(Waiter, slug=slug)
        return waiter


class WaiterNotificationTokenUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WaiterNotificatioTokenUpdateSerialzier

    def get_object(self):
        waiter = self.request.user.waiter
        return waiter


class RestaurantPacpageView(RetrieveAPIView):
    serializer_class = RestaurantPackageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        restaurant = self.request.user.restaurant
        package = restaurant.package
        return package


class UserTypeView(RetrieveAPIView):
    serializer_class = UserTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user

    def get_serializer_class(self):
        user = self.request.user
        if user.user_type == 'restaurant':
            return RestaurantUserTypeSerializer
        return super().get_serializer_class()


class RestaurantCampaignCreateView(generics.CreateAPIView):
    serializer_class = RestaurantCampaignCreateSerializer
    permission_classes = [IsAuthenticated]


class RestaurantCampaignListView(generics.ListAPIView):
    serializer_class = RestaurantCampaignGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.restaurant
        queryset = restaurant.campaigns.all()
        return queryset


class RestaurantCampaignRetrieveView(generics.RetrieveAPIView):
    serializer_class = RestaurantCampaignGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        restaurant = self.request.user.restaurant
        campaign_id = self.kwargs.get('campaign_id')
        campaign = get_object_or_404(restaurant.campaigns, id=campaign_id)
        return campaign


class RestaurantCampaignUpdateView(generics.UpdateAPIView):
    serializer_class = RestaurantCampaignGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        campaign_id = self.kwargs.get('campaign_id')
        campaign = get_object_or_404(RestaurantCampaign, id=campaign_id)
        return campaign


class RestaurantCampaignDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        restaurant = self.request.user.restaurant
        return restaurant

    def delete(self, request, *args, **kwargs):
        restaurant = self.get_object()
        restaurant.campaigns.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RestaurantListView(generics.ListAPIView):
    serializer_class = RestaurantListSerialzier
    permission_classes = [AllowAny]

    def get_queryset(self):
        longitude = self.kwargs.get('longitude')
        latitude = self.kwargs.get('latitude')
        language = self.kwargs.get('langu')
        loyalty_discount_percent = self.request.query_params.get('loyalty_discount_percent')
        name = self.request.query_params.get('name')
        sub_category = self.request.query_params.get('sub_category')
        main_category = self.request.query_params.get('main_category')
        min_average_rating = self.request.query_params.get('min_average_rating')

        queryset = Restaurant.objects.all()
        activate(language)
        if loyalty_discount_percent:
            queryset = queryset.filter(user__is_loyal=True, loyalty_discount_percent=loyalty_discount_percent)

        if name:
            queryset = queryset.filter(user__first_name__icontains=name)

        if sub_category:
            queryset = queryset.filter(category__name__icontains=sub_category)

        if main_category and not sub_category:
            queryset = queryset.filter(category__parent__name__icontains=main_category)

        if min_average_rating:
            queryset = queryset.annotate(average_rating=Avg('reviews__rating'))
            queryset = queryset.filter(average_rating__gte=min_average_rating)

        return queryset


class RestaurantStoryCreateView(generics.CreateAPIView):
    serializer_class = RestaurantStroryCreateSerializer
    permission_classes = [IsAuthenticated]


class RestaurantStoryListView(generics.ListAPIView):
    serializer_class = RestaurantStoryGetSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        slug = self.kwargs.get('restaurant_slug')
        queryset = RestaurantStory.objects.filter(restaurant__slug=slug)
        return queryset


class RestaurantStoryListAllView(generics.ListAPIView):
    serializer_class = RestaurantWithStorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        active_stories_subquery = RestaurantStory.objects.filter(restaurant=OuterRef('pk'), is_activate=True).values(
            'is_activate')[:1]
        queryset = Restaurant.objects.annotate(has_active_stories=Exists(active_stories_subquery)).filter(
            has_active_stories=True)
        return queryset


class RestautantStoryAdminListView(generics.ListAPIView):
    serializer_class = RestaurantStoryGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.restaurant
        queryset = restaurant.stories.all()
        return queryset


class RestaurantStoryUpdateView(generics.UpdateAPIView):
    serializer_class = RestaurantStoryUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        story_id = self.kwargs.get('story_id')
        story = get_object_or_404(RestaurantStory, id=story_id)
        return story


class RestaurantStoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('story_id')
        restaurant = self.request.user.restaurant
        story = get_object_or_404(RestaurantStory, id=id, restaurant=restaurant)
        return story


class RestaurantSearchView(generics.ListAPIView):
    serializer_class = RestaurantListSerialzier
    permission_classes = [AllowAny]

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        name = self.kwargs.get('name')
        queryset = Restaurant.objects.filter(Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name))
        return queryset


class ClientUpdateView(generics.UpdateAPIView):
    serializer_class = ClientUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user


class ClientPasswordUpdateView(generics.UpdateAPIView):
    serializer_class = ClientPasswordUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user


class FavoriteRestaurantCreateView(generics.CreateAPIView):
    serializer_class = FavoriteRestaurantCreateSerializer
    permission_classes = [IsAuthenticated]


class FavoriteRestaurantListView(generics.ListAPIView):
    serializer_class = FavoriteRestaurantListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        client = self.request.user.client
        queryset = client.favorite_restaurants.all()
        return queryset


class FavoriteRestaurantDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('id')
        client = self.request.user.client
        favorite = get_object_or_404(FavoriteRestaurant, client=client, restaurant__id=id)
        return favorite


class RestaurantFbpixelUpdateView(generics.UpdateAPIView):
    serializer_class = RestaurantFbpixelSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        restaurant = self.request.user.restaurant
        return restaurant


class RestaurantFbpixelGetView(generics.RetrieveAPIView):
    serializer_class = RestaurantFbpixelSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        restaurant = self.request.user.restaurant
        return restaurant


class AppleLoginView(APIView):
    def post(self, request):
        client_id = 'com.example.app'  # Replace with your Service ID
        client_secret = generate_apple_client_secret(
            key_id=settings.APPLE_KEY_ID,
            team_id=settings.APPLE_TEAM_ID,
            client_id=client_id,
            private_key=settings.APPLE_PRIVATE_KEY
        )
        code = request.data.get('code')  # Apple authorization code from frontend

        # Exchange code for access token
        token_url = 'https://appleid.apple.com/auth/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://your-backend-url.com/apple/callback/'  # Same as in Apple Developer
        }
        response = requests.post(token_url, data=data)

        if response.status_code == 200:
            token_response = response.json()
            id_token = token_response.get('id_token')

            # Decode the Apple ID token (JWT) to extract user information
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            apple_user_id = decoded['sub']
            email = decoded.get('email')  # Note: email might be null if user hides it

            # Create or retrieve user in your system
            user, created = User.objects.get_or_create(
                apple_user_id=apple_user_id,
                defaults={'username': email or get_random_string(), 'email': email}
            )

            # Serialize user data and return a response
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class RestaurantEventViewSet(viewsets.ModelViewSet):
    queryset = RestaurantEvent.objects.all()
    serializer_class = RestaurantEventSerializer
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['post'], url_path='upload-images')
    def upload_images(self, request, pk=None):
        event = self.get_object()
        files = request.FILES.getlist('image_files')

        if not files:
            return Response(
                {"detail": "No images provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for file in files:
            EventImages.objects.create(event=event, image=file)

        return Response(
            {"detail": "Images uploaded successfully"},
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Handle PUT requests, including image file updates."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class EventGenresList(generics.ListAPIView):
    queryset = EventGenres.objects.all()
    serializer_class = EventGenresSerializer
    permission_classes = [AllowAny]


class EventTypesList(generics.ListAPIView):
    queryset = EventTypes.objects.all()
    serializer_class = EventTypeSerializer
    permission_classes = [AllowAny]


class RestaurantCategoryList(generics.ListAPIView):
    queryset = RestaurantCategory.objects.all()
    serializer_class = RestaurantCategorySerializer
    permission_classes = [AllowAny]


class RestaurantSubCategoryList(generics.ListAPIView):
    queryset = RestaurantSubCategory.objects.all()
    serializer_class = RestaurantSubCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RestaurantSubCategoryFilter
    permission_classes = [AllowAny]


class ClientInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Client Details",
        description="Retrieve the detailed information of the authenticated client's profile.",
        responses=ClientSerializer
    )
    def get(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(user=request.user)
            serializer = ClientSerializer(client)
            return Response(serializer.data, status=200)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=404)


class UpdateFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user

        if not hasattr(user, 'client'):
            return Response(
                {"detail": "Only clients can update FCM token."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = FCMTokenUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "FCM token successfully updated."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
Loyalty part will be replaced to main codes part
"""
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import LoyalUser
from .serializers import LoyalUserRegisterSerializer, LoyalUserLoginSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class LoyalUserRegisterView(GenericAPIView):
    serializer_class = LoyalUserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loyal_user = serializer.save()

        return Response({
            "user": {
                "id": loyal_user.id,
                "first_name": loyal_user.first_name,
                "last_name": loyal_user.last_name,
                "email": loyal_user.user.email
            }
        }, status=status.HTTP_201_CREATED)


class LoyalUserLoginView(GenericAPIView):
    serializer_class = LoyalUserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        loyal_user = serializer.validated_data["user"]
        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        return Response({
            "user": {
                "first_name": loyal_user.first_name,
                "last_name": loyal_user.last_name,
                "phone": loyal_user.phone,
                "email": loyal_user.user.email,
                "birthday_date": loyal_user.birthday_date,
                "address": loyal_user.address
            },
            "refresh": refresh,
            "access": access,
        }, status=status.HTTP_200_OK)


class OTPVerificationView(generics.UpdateAPIView):
    serializer_class = OTPVerificationSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CreateLoyalCardView(generics.CreateAPIView):
    serializer_class = LoyalCardCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """Serializer-ə request-i ötürmək üçün konteksti qaytarır."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context