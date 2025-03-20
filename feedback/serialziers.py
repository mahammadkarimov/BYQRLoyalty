from rest_framework import serializers
from django.utils import timezone
from calendar import monthrange
import json
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Feedback, FeedbackDescription, Question
import base64
from io import BytesIO
from django.core.files.base import ContentFile

User = get_user_model()

class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'id',
            'question_az',
            'question_tr',
            'question_ar',
            'question_en',
            'question_ru',
            'question_ko',
            'created_at'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        user = self.context['request'].user
        question = Question.objects.create(**validated_data, user=user)
        return question


class FeedbackQuestionGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'id',
            'question',
            'created_at'
        )


class FeedbackDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackDescription
        fields = ['description', 'overall_rating']


class GlobalFeedbackSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    rating = serializers.IntegerField()
    review = serializers.CharField()
    image = serializers.CharField(required=False)

    def validate_question(self, value):
        if not Question.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid question ID.")
        return value


class FeedbackBulkCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    overall_rating = serializers.IntegerField()
    instance = serializers.CharField()
    feedbacks = GlobalFeedbackSerializer(many=True)

    def create(self, validated_data):
        feedbacks_data = validated_data.pop('feedbacks')
        username = validated_data.pop('username')
        user = get_object_or_404(User, username=username)
        feedback_description = FeedbackDescription.objects.create(**validated_data, user=user)

        feedbacks = []
        for feedback_data in feedbacks_data:
            if feedback_data.get('image'):
                try:
                    format, imgstr = feedback_data['image'].split(';base64,')
                    ext = format.split('/')[-1]
                    image_data = ContentFile(base64.b64decode(imgstr), name=f"image.{ext}")
                    feedback_data['image'] = image_data
                except Exception as e:
                    raise serializers.ValidationError("Invalid image format.")

            question_id = feedback_data.pop("question")
            question = get_object_or_404(Question, id=question_id)

            feedback = Feedback.objects.create(
                question=question,
                description=feedback_description,
                rating=feedback_data.get('rating'),
                review=feedback_data.get('review'),
                image=feedback_data.get('image')
            )
            feedback.save()

        return {
            'feedback_description': feedback_description,
            'feedbacks': feedbacks
        }
class GlobalFeedbackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackDescription
        fields = (
            'id',
            'instance',
            'description',
            'overall_rating',
            'created_at'
        )


class GlobalFeedbackAnswerListSerializer(serializers.ModelSerializer):
    instance = serializers.CharField(source='description.instance')
    description = serializers.CharField(source='description.description')
    created_at = serializers.DateTimeField(source='description.created_at')
    class Meta:
        model = Feedback
        fields = (
            'id',
            'instance',
            'description',
            'rating',
            'review',
            'image',
            'created_at'
        )


class FeedbackInQuestionSerialzier(serializers.ModelSerializer):
    instance = serializers.CharField(source='description.instance')
    created_at = serializers.DateTimeField(source='description.created_at')
    class Meta:
        model = Feedback
        fields = (
            'id',
            'rating',
            'review',
            'image',
            'instance',
            'created_at'
        )


class GlobalQuestionWithAnswersSerialzier(serializers.ModelSerializer):
    feedbacks = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = (
            'id',
            'question_az',
            'question_tr',
            'question_ar',
            'question_en',
            'question_ru',
            'question_ko',
            'created_at',
            'feedbacks'
        )

    def get_feedbacks(self, obj):
        if hasattr(obj, 'filtered_feedbacks'):
            return FeedbackInQuestionSerialzier(obj.filtered_feedbacks, many=True).data
        return FeedbackInQuestionSerialzier(obj.feedbacks, many=True).data


class GlobalFeedbackDescriptionStatisticSerializer(serializers.ModelSerializer):
    daily_feedbacks = serializers.SerializerMethodField()
    weekly_feedbacks = serializers.SerializerMethodField()
    monthly_feedbacks = serializers.SerializerMethodField()
    total_feedbacks = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackDescription
        fields = ('daily_feedbacks', 'weekly_feedbacks', 'monthly_feedbacks', 'total_feedbacks')

    def get_daily_feedbacks(self, obj):
        user=self.context['request'].user
        today = timezone.now().date()
        return FeedbackDescription.objects.filter(created_at__date=today, user=user).count()

    def get_weekly_feedbacks(self, obj):
        user=self.context['request'].user
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())
        week_end = week_start + timezone.timedelta(days=6)
        return FeedbackDescription.objects.filter(created_at__date__range=[week_start, week_end], user=user).count()

    def get_monthly_feedbacks(self, obj):
        user=self.context['request'].user
        today = timezone.now().date()
        month_start = today.replace(day=1)
        month_end = today.replace(day=monthrange(today.year, today.month)[1])
        return FeedbackDescription.objects.filter(created_at__date__range=[month_start, month_end], user=user).count()

    def get_total_feedbacks(self, obj):
        user=self.context['request'].user
        return FeedbackDescription.objects.filter(user=user).count()