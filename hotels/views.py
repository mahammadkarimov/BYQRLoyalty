from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from calendar import monthrange
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.generics import (
    CreateAPIView, 
    ListAPIView,
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView, 
    RetrieveAPIView, 
    UpdateAPIView, 
    DestroyAPIView)
from .serializers import (
    ServiceGetSerializer, 
    ServiceUpdateDeleteSerialzier, 
    ServiceCreateSerializer,
    RestaurantListSerializer,
    CustomerServiceGetSerializer,
    CustomerServiceDetailSerializer,
    CustomerServiceUpdateSerialzier,
    CustomerServiceCreateSerializer,
    CustomerServiceClientDetailSerializer,
    CustomerServiceClientGetSerializer,
    ServiceClientGetSerializer,
    QuestionCreateAdminSerializer,
    FeedbackDescriptionSerializer,
    FeedbackSerializer,
    BulkFeedbackCreateSerializer,
    QuestionGetSerializer,
    HotelRoomCreateUpdateSerialzier,
    HotelRoomGetSerialzier,
    FeedbackListSerializer,
    FeedbackAnswerListSerializer,
    QuestionWithAnswersSerialzier,
    FeedbackDescriptionStatisticSerializer
)
from .models import TechnicalService, Service, Question, HotelRoom, FeedbackDescription, Feedback
from django.shortcuts import get_object_or_404, get_list_or_404
from base_user.models import Restaurant, Hotel
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import activate
# Create your views here.

User = get_user_model()


class ServiceRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceUpdateDeleteSerialzier
    permission_classes = [IsAuthenticated]
    queryset = TechnicalService.objects.all()

    def get_object(self):
        slug = self.kwargs.get('slug')
        service = get_object_or_404(TechnicalService, slug=slug)
        return service
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceGetSerializer
        return super().get_serializer_class()


class ServiceClientDetailView(RetrieveAPIView):
    serializer_class = ServiceClientGetSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        slug = self.kwargs.get('slug')
        service = get_object_or_404(TechnicalService, slug=slug)
        return service


class ServiceListView(ListAPIView):
    serializer_class = ServiceClientGetSerializer
    queryset = TechnicalService.objects.all()
    permission_classes = [AllowAny]

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        username = self.kwargs.get('username')
        services = TechnicalService.objects.filter(hotel__user__username=username).order_by('order_number')
        return services


class ServiceCreateView(CreateAPIView):
    serializer_class = ServiceCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = TechnicalService.objects.all()


class RestaurantListView(ListAPIView):
    serializer_class = RestaurantListSerializer
    permission_classes = [AllowAny]
    queryset = Restaurant.objects.all()

    def get_queryset(self):
        name = self.kwargs.get('username')
        user = get_object_or_404(User, username=name)
        restaurants = Restaurant.objects.filter(hotel=user.hotel)
        print(restaurants)
        return restaurants
    

class AdminServiceListView(ListAPIView):
    serializer_class = ServiceGetSerializer
    queryset = TechnicalService.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        services = TechnicalService.objects.filter(hotel=user.hotel)
        return services
    

class CustomerServiceCreateView(CreateAPIView):
    serializer_class = CustomerServiceCreateSerializer
    permission_classes = [IsAuthenticated]


class CustomerServiceListView(ListAPIView):
    serializer_class = CustomerServiceClientGetSerializer
    queryset = Service.objects.all()
    permission_classes = [AllowAny]

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        username = self.kwargs.get('username')
        print(username)
        services = Service.objects.filter(hotel__user__username = username)
        print(services)
        return services


class CustomerServiceDetailView(RetrieveAPIView):
    serializer_class = CustomerServiceDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs.get('slug')
        service = get_object_or_404(Service, slug=slug)
        return service
    

class CustomerServiceClientDetailView(RetrieveAPIView):
    serializer_class = CustomerServiceClientDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        slug = self.kwargs.get('slug')
        service = get_object_or_404(Service, slug=slug)
        return service


class CustomerServiceAdminListView(ListAPIView):
    serializer_class = CustomerServiceGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.all()

    def get_queryset(self):
        hotel = self.request.user.hotel
        services = Service.objects.filter(hotel=hotel)
        return services
    

class CustomerServiceAdminUpdateView(UpdateAPIView):
    serializer_class = CustomerServiceUpdateSerialzier
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        slug = self.kwargs.get('slug')
        service = get_object_or_404(Service, slug=slug)
        return service
    

class CustomerServiceAdminDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get('slug')
        service = get_object_or_404(Service, slug=slug)
        return service


class QuestionListCreateView(ListCreateAPIView):
    serializer_class = QuestionCreateAdminSerializer
    permission_classes = [IsAuthenticated]
    queryset = Question.objects.all()

    def get_queryset(self):
        hotel = self.request.user.hotel
        queryset = hotel.questions.all()
        return queryset
    

class QuestionListView(ListAPIView):
    serializer_class = QuestionGetSerializer
    permission_classes = [AllowAny]
    queryset = Question.objects.all()

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        username = self.kwargs.get('username')
        hotel = get_object_or_404(Hotel, user__username=username)
        queryset = hotel.questions.all()
        return queryset


class QuestionRetriveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionCreateAdminSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=id)
        return question
    

class BulkFeedbackCreateView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        request_body=BulkFeedbackCreateSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Feedback and FeedbackDescription created",
                examples={
                    "application/json": {
                        "status": "success",
                        "data": {
                            "feedback_description": {
                                "description": "Great service and amenities.",
                                "overall_rating": 5,
                                "room_id": "room_101"
                            },
                            "feedbacks": [
                                {
                                    "question": 1,
                                    "rating": 4,
                                    "description": 1
                                },
                                {
                                    "question": 2,
                                    "rating": 5,
                                    "description": 1
                                }
                            ]
                        }
                    }
                },
            ),
            status.HTTP_400_BAD_REQUEST: "Invalid data",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = BulkFeedbackCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({'status': 'success', 'data': {
                'feedback_description': FeedbackDescriptionSerializer(result['feedback_description']).data,
                'feedbacks': FeedbackSerializer(result['feedbacks'], many=True).data
            }}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HotelRoomListCreateView(ListCreateAPIView):
    serializer_class = HotelRoomCreateUpdateSerialzier
    queryset = HotelRoom.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        hotel = self.request.user.hotel
        queryset = hotel.rooms.all()
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return HotelRoomGetSerialzier
        return super().get_serializer_class()


class HotelRoomRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = HotelRoomCreateUpdateSerialzier
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('id')
        room = get_object_or_404(HotelRoom, id=id)
        return room
    

class FeedbackListView(ListAPIView):
    serializer_class = FeedbackListSerializer
    permission_classes = [IsAuthenticated]
    queryset = FeedbackDescription.objects.all()

    def get_queryset(self):
        hotel = self.request.user.hotel
        created_at = self.request.GET.get('created_at')
        today = timezone.now().date()
        queryset = FeedbackDescription.objects.filter(room__hotel=hotel)
        if created_at == 'today':
            queryset = FeedbackDescription.objects.filter(room__hotel=hotel, created_at__date=today)
        elif created_at == 'week':
            week_start = today - timezone.timedelta(days=today.weekday())
            week_end = week_start + timezone.timedelta(days=6)
            queryset = FeedbackDescription.objects.filter(room__hotel=hotel, created_at__date__range=[week_start, week_end])
        elif created_at == 'month':
            month_start = today.replace(day=1)
            month_end = today.replace(day=monthrange(today.year, today.month)[1])
            queryset = FeedbackDescription.objects.filter(room__hotel=hotel, description__created_at__date__range=[month_start, month_end])
        return queryset


class FeedbackAnswersListByQuestionView(ListAPIView):
    serializer_class = FeedbackAnswerListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Feedback.objects.all()

    def get_queryset(self):
        id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=id)
        queryset = Feedback.objects.filter(question=question)
        return queryset


class HotelRoomGetByNameView(RetrieveAPIView):
    serializer_class = HotelRoomGetSerialzier
    permission_classes = [AllowAny]

    def get_object(self):
        username = self.kwargs.get('username')
        name = self.kwargs.get('name')
        room = get_object_or_404(HotelRoom, name=name, hotel__user__username=username)
        return room


class QuestionWithAnswersListView(ListAPIView):
    serializer_class = QuestionWithAnswersSerialzier
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        hotel = self.request.user.hotel
        created_at = self.request.GET.get('created_at')
        queryset = hotel.questions.all()
        today = timezone.now().date()
        if created_at == 'today':
            feedbacks_prefetch = Prefetch(
                'feedbacks',
                queryset=Feedback.objects.filter(description__room__hotel=hotel, description__created_at__date=today),
                to_attr='filtered_feedbacks'
            )
            queryset = hotel.questions.prefetch_related(feedbacks_prefetch)
        elif created_at == 'week':
            week_start = today - timezone.timedelta(days=today.weekday())
            week_end = week_start + timezone.timedelta(days=6)
            feedbacks_prefetch = Prefetch(
                'feedbacks',
                queryset=Feedback.objects.filter(description__room__hotel=hotel, description__created_at__date__range=[week_start, week_end]),
                to_attr='filtered_feedbacks'
            )
            queryset = hotel.questions.prefetch_related(feedbacks_prefetch)
        elif created_at == 'month':
            month_start = today.replace(day=1)
            month_end = today.replace(day=monthrange(today.year, today.month)[1])
            feedbacks_prefetch = Prefetch(
                'feedbacks',
                queryset=Feedback.objects.filter(description__room__hotel=hotel, description__created_at__date__range=[month_start, month_end]),
                to_attr='filtered_feedbacks'
            )
            queryset = hotel.questions.prefetch_related(feedbacks_prefetch)           
        return queryset
    

class FeedbackStatisticView(RetrieveAPIView):
    serializer_class = FeedbackDescriptionStatisticSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        feedback = FeedbackDescription.objects.first()
        return feedback