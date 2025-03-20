import math
import uuid
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from base_user.models import Restaurant
from .models import MealCategory, Meal, SubCategory, MealImage, MealSize, BasketItem, Basket, Order, FavoriteMeal
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend, filters
import django_filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils.text import slugify
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, RetrieveAPIView, \
    UpdateAPIView, DestroyAPIView, CreateAPIView
from django.utils.translation import activate
from .filters import MealFilter
from .serializers import (
    MealCategorySerializer,
    MealSerializer,
    GetMealSerializer,
    GetMealAdminSerializer,
    MealAdminSerializer,
    ScanQRSerializer,
    CreateMealSerializer,
    GeoLocationSerializer,
    SubCategorySerializer,
    GetSubCategorySerializer,
    GetSubCategoryClientSerializer,
    MealUpdateSerialzier,
    MealCategoryHotelAdminSerializer,
    SubCategoryHotelAdminSerializer,
    CreateMealHotelAdminSerializer,
    MealImagesUpdateSerialzier,
    MealImageCreateSerialzier,
    MealVideoSerializer,
    MealSizeSerializer,
    RestaurantSocialMediaSerializer,
    RestaurantSocialMediaReviewSerializer,
    RestaurantSocialMediaAdminSerializer,
    RestaurantSocialMediaUpdateSerializer,
    BasketItemCreateSeriazlier,
    OrderSerializer,
    OrderCreateSerializer,
    BasketItemUpdateSerializer,
    BasketSerializer,
    FavoriteMealCreateSerializer,
    FavoriteMealSerialzier, RestaurantMobileDetailsSerializer, RestaurantMobileMealsSerializer, MealPrioritySerializer
)

User = get_user_model()


class MealCategoryViewSet(ModelViewSet):
    parser_classes = (MultiPartParser, FormParser,)
    lookup_field = "slug"
    queryset = MealCategory.objects.all().order_by("order")
    serializer_class = MealCategorySerializer
    permission_classes = (IsAuthenticated,)

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return []
    #     return super().get_permissions()

    def create(self, request, *args, **kwargs):
        lang = self.kwargs.get('lang_code')
        print(lang)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(created_from=request.user.restaurant))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MealCategoryListCreateView(ListCreateAPIView):
    serializer_class = MealCategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = MealCategory.objects.all()

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        restaurant = self.request.user.restaurant
        queryset = MealCategory.objects.filter(created_from=restaurant)
        return queryset

    def create(self, request, *args, **kwargs):
        language = self.kwargs.get('lang')
        print(language)
        return super().create(request, *args, **kwargs)


class MealCategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = MealCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        language = self.kwargs.get('lang')
        activate(language)
        slug = self.kwargs.get('slug')
        category = get_object_or_404(MealCategory, slug=slug)
        return category


class SubCategoryViewSet(ModelViewSet):
    parser_classes = (MultiPartParser, FormParser,)
    lookup_field = "slug"
    queryset = SubCategory.objects.all().order_by("order")
    serializer_class = SubCategorySerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(created_from=request.user.restaurant))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubCategoryListCreateView(ListCreateAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = SubCategory.objects.all()

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        restaurant = self.request.user.restaurant
        queryset = SubCategory.objects.filter(created_from=restaurant)
        return queryset

    def create(self, request, *args, **kwargs):
        language = self.kwargs.get('lang')
        activate(language)
        return super().create(request, *args, **kwargs)


class SubCategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        language = self.kwargs.get('lang')
        activate(language)
        slug = self.kwargs.get('slug')
        category = get_object_or_404(SubCategory, slug=slug)
        return category


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Meal
        fields = ["category"]


class MealViewSet(ModelViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser,)
    lookup_field = "slug"
    queryset = Meal.objects.all().order_by('-id')
    serializer_class = MealSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return GetMealSerializer
        elif self.action == 'create':
            return CreateMealSerializer
        else:
            return MealSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(created_from=request.user.restaurant))
        serializer = GetMealSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = (AllowAny,)
        instance = self.get_object()
        serializer = GetMealSerializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='search/(?P<username>[^/.]+)')
    def search(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = Meal.objects.filter(created_from=user.restaurant)
        serializer = MealSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MealListCreateView(ListCreateAPIView):
    serializer_class = GetMealAdminSerializer
    permission_classes = [IsAuthenticated]
    queryset = Meal.objects.all()

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        restaurant = self.request.user.restaurant
        queryset = Meal.objects.filter(created_from=restaurant)
        return queryset

    def create(self, request, *args, **kwargs):
        language = self.kwargs.get('lang')
        activate(language)
        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateMealSerializer
        return super().get_serializer_class()


class MealRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = MealAdminSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('slug')
        meal = get_object_or_404(Meal, slug=slug)
        return meal

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetMealAdminSerializer
        return super().get_serializer_class()


class MealListByUsernameView(ListAPIView):
    serializer_class = GetMealSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        queryset = Meal.objects.filter(created_from=restaurant)
        return queryset


class QRCodeViewSet(ModelViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser,)
    lookup_field = "user__username"
    queryset = Restaurant.objects.all()
    serializer_class = ScanQRSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        created_from = self.kwargs.get('created_from')
        queryset = self.filter_queryset(self.get_queryset().filter(created_from=created_from))
        serializer = ScanQRSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), **self.kwargs)
        serializer = ScanQRSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='(?P<username>[^/.]+)/(?P<slug>[^/.]+)')
    def get_meals_by_category(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        category_slug = self.kwargs.get('slug')

        # Get user and meal category based on username and category slug
        user = get_object_or_404(User, username=username)
        meal_category = get_object_or_404(MealCategory, slug=category_slug)

        # Get and sort subcategories that have meals and are related to the meal category
        subcategories = SubCategory.objects.filter(
            main_category=meal_category,
            meals__created_from=user.restaurant,
            meals__isnull=False
        ).distinct().order_by('order')

        # Serialize the subcategories data, which includes related meals
        serializer = GetSubCategorySerializer(subcategories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='meals-by-username/(?P<username>[^/.]+)/(?P<slug>[^/.]+)')
    def get_meals_by_username(self, request, *args, **kwargs):
        # Retrieve username and category_slug from URL parameters
        username = self.kwargs.get('username')
        meal_slug = self.kwargs.get('slug')
        # Get user based on username
        user = get_object_or_404(User, username=username)

        # Get meals related to the specified category_slug
        meals_queryset = Meal.objects.filter(slug=meal_slug, created_from=user.restaurant)

        # Serialize the meals data
        serializer = MealSerializer(meals_queryset, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='search/(?P<username>[^/.]+)/(?P<name>[^/.]+)')
    def search(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        name = self.kwargs.get('name').strip()  # Remove any leading/trailing whitespace
        user = get_object_or_404(User, username=username)
        queryset = Meal.objects.filter(name__icontains=name, created_from=user.restaurant)
        serializer = MealSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class QrListByUsernameView(RetrieveAPIView):
    serializer_class = ScanQRSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        language = self.kwargs.get('lang')
        activate(language)
        username = self.kwargs.get('username')

        restaurant = get_object_or_404(
            Restaurant.objects.select_related(
                'user',
                'package'
            ).prefetch_related(
                'language',
                'currency',
                'campaigns',
                'workinghours'
            ),
            user__username=username
        )
        return restaurant


class MealSearchView(ListAPIView):
    serializer_class = MealSerializer
    permission_classes = [AllowAny]
    queryset = Meal.objects.all()

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        name = self.kwargs.get('name')
        queryset = Meal.objects.filter(name__icontains=name, created_from=restaurant)
        return queryset


class QrRetrieveBySlugView(RetrieveAPIView):
    serializer_class = MealSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        language = self.kwargs.get('lang')
        activate(language)
        slug = self.kwargs.get('slug')
        meal = get_object_or_404(Meal, slug=slug)
        return meal


class QrSubCategoryListView(ListAPIView):
    serializer_class = GetSubCategoryClientSerializer
    permission_classes = [AllowAny]
    queryset = SubCategory.objects.all()

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        username = self.kwargs.get('username')
        category_slug = self.kwargs.get('slug')

        # Get user and meal category based on username and category slug
        user = get_object_or_404(User, username=username)
        meal_category = get_object_or_404(MealCategory, slug=category_slug)

        # Get and sort subcategories that have meals and are related to the meal category
        subcategories = SubCategory.objects.filter(
            main_category=meal_category,
            meals__created_from=user.restaurant,
            meals__isnull=False
        ).distinct().order_by('order')
        return subcategories


class DistanceView(APIView):

    def get_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0710
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(
            math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = R * c
        distance_meters = distance_km * 1000
        return distance_meters

    @swagger_auto_schema(
        request_body=GeoLocationSerializer,
        responses={200: openapi.Response('Response', GeoLocationSerializer)}
    )
    def post(self, request, *args, **kwargs):
        serializer = GeoLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = request.data.get('username')  # Get username from request
        if not username:
            return Response({'error': 'Username is required'}, status=400)

        try:
            user_data = User.objects.get(username=username)
            user = Restaurant.objects.get(user=user_data)
        except Restaurant.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        distance = self.get_distance(user.latitude, user.longitude, serializer.validated_data['latitude'],
                                     serializer.validated_data['longitude'])

        return Response({'distance': distance, 'distance_area': user.distance_area}, status=200)


class HotelRestaurantAdminMealListCreateView(ListCreateAPIView):
    serializer_class = GetMealAdminSerializer
    permission_classes = [IsAuthenticated]
    queryset = Meal.objects.order_by("priority")

    def get_queryset(self):
        username = self.kwargs.get('restaurant_username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        queryset = Meal.objects.filter(created_from=restaurant).order_by("priority")
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['restaurant'] = self.kwargs['restaurant_username']
        return context

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateMealHotelAdminSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        username = self.kwargs.get('restaurant_username')
        restaurant = get_object_or_404(Restaurant, user__username=username)

        meal_name = request.data.get('name_az')
        meal_price = request.data.get('price')

        if Meal.objects.filter(name_az=meal_name, price=meal_price, created_from=restaurant).exists():
            raise ValidationError({"detail": "A meal with this name and price already exists."})

        return super().create(request, *args, **kwargs)


class HotelRestaurantAdminMealGetUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = MealAdminSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('meal_slug')
        language = self.request.query_params.get('lang')
        activate(language)
        meal = get_object_or_404(Meal, slug=slug)
        return meal

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HotelRestaurantAdminCategoryListByUsernameView(ListCreateAPIView):
    serializer_class = MealCategoryHotelAdminSerializer
    permission_classes = [IsAuthenticated]
    queryset = MealCategory.objects.all()

    def get_queryset(self):
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        queryset = MealCategory.objects.filter(created_from=restaurant)
        return queryset

    def perform_create(self, serializer):
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        serializer.save(created_from=restaurant)
        return super().perform_create(serializer)


class HotelRestaurantAdminCategoryRetriveUpdateDestroyByUsernameView(RetrieveUpdateDestroyAPIView):
    serializer_class = MealCategoryHotelAdminSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('slug')
        mealcategory = get_object_or_404(MealCategory, slug=slug)
        return mealcategory


class HotelRestaurantAdminSubCategoryListByUsernameView(ListCreateAPIView):
    serializer_class = SubCategoryHotelAdminSerializer
    permission_classes = [IsAuthenticated]
    queryset = SubCategory.objects.all()

    def get_queryset(self):
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        queryset = SubCategory.objects.filter(created_from=restaurant)
        return queryset

    def perform_create(self, serializer):
        language = self.kwargs.get('lang')
        activate(language)
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        serializer.save(created_from=restaurant)
        return super().perform_create(serializer)


class HotelRestaurantAdminSubCategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = SubCategoryHotelAdminSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('slug')
        language = self.request.query_params.get('lang')
        activate(language)
        subcategory = get_object_or_404(SubCategory, slug=slug)
        return subcategory

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'lang',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MealImageUpdateView(UpdateAPIView):
    serializer_class = MealImagesUpdateSerialzier
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('image_id')
        image = get_object_or_404(MealImage, id=id)
        return image


class MealImageCreateView(CreateAPIView):
    serializer_class = MealImageCreateSerialzier
    permission_classes = [AllowAny]


class MealImageDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('image_id')
        image = get_object_or_404(MealImage, id=id)
        return image


class MealVideoUpdateDeleteView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealVideoSerializer

    def get_object(self):
        slug = self.kwargs.get('meal_slug')
        meal = get_object_or_404(Meal, slug=slug)
        return meal


class MealSizeUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealSizeSerializer

    def get_object(self):
        id = self.kwargs.get("size_id")
        size = get_object_or_404(MealSize, id=id)
        return size


class MealSizeDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("size_id")
        size = get_object_or_404(MealSize, id=id)
        return size


class MealSearchView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = MealSerializer
    queryset = Meal.objects.all()

    def get_queryset(self):
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        name = self.kwargs.get('name')
        lang = self.kwargs.get('lang')
        activate(lang)
        queryset = Meal.objects.filter(created_from=restaurant, name__icontains=name)
        return queryset


class MealFilterListView(ListAPIView):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MealFilter


class RestaurantSocialMediaGetView(RetrieveAPIView):
    serializer_class = RestaurantSocialMediaAdminSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        restaurant = self.request.user.restaurant
        return restaurant


class RestaurantSocialMediaUpdateView(UpdateAPIView):
    serializer_class = RestaurantSocialMediaUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        restaurant = self.request.user.restaurant
        return restaurant


class RestaurantSocialMediaReviewRetrieveView(RetrieveAPIView):
    serializer_class = RestaurantSocialMediaReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        restaurant = self.request.user.restaurant
        return restaurant


class RestaurantSocialMediaReviewUpdateView(UpdateAPIView):
    serializer_class = RestaurantSocialMediaReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        restaurant = self.request.user.restaurant
        return restaurant


class BasketItemCreateView(CreateAPIView):
    serializer_class = BasketItemCreateSeriazlier
    permission_classes = [IsAuthenticated]


class BasketItemUpdateView(UpdateAPIView):
    serializer_class = BasketItemUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('id')
        basket_item = get_object_or_404(BasketItem, id=id)
        return basket_item


class BasketItemDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('id')
        basket_item = get_object_or_404(BasketItem, id=id)
        return basket_item


class BasketGetView(RetrieveAPIView):
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        client = self.request.user.client
        try:
            basket = Basket.objects.get(client=client, is_completed=False)
        except Basket.DoesNotExist:
            raise NotFound("Basket not found for the current user.")
        return basket


class OrderCreateView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]


class OrderGetView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        client = self.request.user.client
        order = get_object_or_404(Order, client=client, is_completed=False)
        return order


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        client = self.request.user.client
        queryset = Order.objects.filter(client=client, is_completed=True)
        return queryset


class FavoriteMealCreateView(CreateAPIView):
    serializer_class = FavoriteMealCreateSerializer
    permission_classes = [IsAuthenticated]


class FavoriteMealListView(ListAPIView):
    serializer_class = FavoriteMealSerialzier
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        client = self.request.user.client
        queryset = client.favorites.filter(meal__created_from=restaurant)
        return queryset


class FavoriteMealDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('id')
        client = self.request.user.client
        favorite = get_object_or_404(FavoriteMeal, meal__id=id, client=client)
        return favorite


class AllFavoriteMealListView(ListAPIView):
    serializer_class = FavoriteMealSerialzier
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        language = self.kwargs.get('lang')
        activate(language)
        client = self.request.user.client
        queryset = client.favorites.all()
        return queryset





class RestaurantMealsView(RetrieveAPIView):

    serializer_class = RestaurantMobileMealsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        language = self.kwargs.get('lang')
        activate(language)
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        return restaurant



class RestaurantDetailsView(RetrieveAPIView):
    serializer_class = RestaurantMobileDetailsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        language = self.kwargs.get('lang')
        activate(language)
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        return restaurant


class BulkMealUpdateView(APIView):

    def patch(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Request data must be a list of objects"}, status=status.HTTP_400_BAD_REQUEST)

        updated_meals = []
        for item in data:
            meal_id = item.get("id")
            if not meal_id:
                return Response({"error": "Each object must have an 'id' field"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                meal = Meal.objects.get(id=meal_id)
            except Meal.DoesNotExist:
                return Response({"error": f"Meal with id {meal_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

            serializer = MealPrioritySerializer(meal, data=item, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_meals.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"updated_meals": updated_meals}, status=status.HTTP_200_OK)