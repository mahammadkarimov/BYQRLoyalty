from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from django.utils.translation import activate
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg import openapi
from django.utils import timezone
from calendar import monthrange
from django.db.models import Prefetch
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Question, Feedback, FeedbackDescription
from django.contrib.auth import get_user_model
from .serialziers import (
    QuestionCreateSerializer,
    FeedbackQuestionGetSerializer,
    GlobalQuestionWithAnswersSerialzier,
    GlobalFeedbackAnswerListSerializer,
    FeedbackDescriptionSerializer,
    GlobalFeedbackDescriptionStatisticSerializer,
    GlobalFeedbackListSerializer,
    GlobalFeedbackSerializer,
    FeedbackBulkCreateSerializer,
    FeedbackInQuestionSerialzier
)

User = get_user_model()

# Create your views here.
class QuestionListCreateView(ListCreateAPIView):
    serializer_class = QuestionCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Question.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = user.questions.all()
        return queryset
    

class QuestionListView(ListAPIView):
    serializer_class = FeedbackQuestionGetSerializer
    permission_classes = [AllowAny]
    queryset = Question.objects.all()

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        activate(lang)
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = user.questions.all()
        return queryset


class QuestionRetriveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=id)
        return question
    

class BulkFeedbackCreateView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=FeedbackBulkCreateSerializer,
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
                                "instance": "M15"
                            },
                            "feedbacks": [
                                {
                                    "question": 1,
                                    "rating": 4,
                                    "review": "string",
                                    "image": "string",
                                    "description": 1
                                },
                                {
                                    "question": 2,
                                    "rating": 5,
                                    "review": "string",
                                    "image": "string",
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
        print(request.data)
        serializer = FeedbackBulkCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'status': 'success',
                'data': {
                    'feedback_description': FeedbackDescriptionSerializer(result['feedback_description']).data,
                    'feedbacks': GlobalFeedbackSerializer(result['feedbacks'], many=True).data
                }
            }, status=status.HTTP_201_CREATED)
        print("Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FeedbackListView(ListAPIView):
    serializer_class = GlobalFeedbackListSerializer
    permission_classes = [IsAuthenticated]
    queryset = FeedbackDescription.objects.all()

    def get_queryset(self):
        user = self.request.user
        created_at = self.request.GET.get('created_at')
        today = timezone.now().date()
        queryset = FeedbackDescription.objects.filter(user=user)
        if created_at == 'today':
            queryset = FeedbackDescription.objects.filter(user=user, created_at__date=today)
        elif created_at == 'week':
            week_start = today - timezone.timedelta(days=today.weekday())
            week_end = week_start + timezone.timedelta(days=6)
            queryset = FeedbackDescription.objects.filter(user=user, created_at__date__range=[week_start, week_end])
        elif created_at == 'month':
            month_start = today.replace(day=1)
            month_end = today.replace(day=monthrange(today.year, today.month)[1])
            queryset = FeedbackDescription.objects.filter(user=user, description__created_at__date__range=[month_start, month_end])
        return queryset


class FeedbackAnswersListByQuestionView(ListAPIView):
    serializer_class = GlobalFeedbackAnswerListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Feedback.objects.all()

    def get_queryset(self):
        id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=id)
        queryset = Feedback.objects.filter(question=question)
        return queryset


class QuestionWithAnswersListView(ListAPIView):
    serializer_class = GlobalQuestionWithAnswersSerialzier
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        created_at = self.request.GET.get('created_at')
        queryset = user.questions.all()
        today = timezone.now().date()
        if created_at == 'today':
            feedbacks_prefetch = Prefetch(
                'feedbacks',
                queryset=Feedback.objects.filter(description__user=user, description__created_at__date=today),
                to_attr='filtered_feedbacks'
            )
            queryset = user.questions.prefetch_related(feedbacks_prefetch)
        elif created_at == 'week':
            week_start = today - timezone.timedelta(days=today.weekday())
            week_end = week_start + timezone.timedelta(days=6)
            feedbacks_prefetch = Prefetch(
                'feedbacks',
                queryset=Feedback.objects.filter(description__user=user, description__created_at__date__range=[week_start, week_end]),
                to_attr='filtered_feedbacks'
            )
            queryset = user.questions.prefetch_related(feedbacks_prefetch)
        elif created_at == 'month':
            month_start = today.replace(day=1)
            month_end = today.replace(day=monthrange(today.year, today.month)[1])
            feedbacks_prefetch = Prefetch(
                'feedbacks',
                queryset=Feedback.objects.filter(description__user=user, description__created_at__date__range=[month_start, month_end]),
                to_attr='filtered_feedbacks'
            )
            queryset = user.questions.prefetch_related(feedbacks_prefetch)           
        return queryset
    

class FeedbackStatisticView(RetrieveAPIView):
    serializer_class = GlobalFeedbackDescriptionStatisticSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        feedback = FeedbackDescription.objects.first()
        return feedback


class FeedbackretrieveView(RetrieveAPIView):
    serializer_class = FeedbackInQuestionSerialzier
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("id")
        feedback = get_object_or_404(Feedback, id=id)
        return feedback