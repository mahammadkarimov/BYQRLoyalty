from rest_framework import serializers
from django.utils import timezone
from .models import TechnicalService, Service, Question, FeedbackDescription, Feedback, HotelRoom, ServiceImages
from calendar import monthrange
from django.contrib.auth import get_user_model
from base_user.models import Restaurant, Hotel
from django.utils.text import slugify
import uuid

User = get_user_model()


class ServiceGetSerializer(serializers.ModelSerializer):
    hotel = serializers.CharField(source='hotel.user.username')

    class Meta:
        model = TechnicalService
        fields = (
            'id',
            'title_az',
            'title_tr',
            'title_ar',
            'title_en',
            'title_ru',
            'title_ko',
            'icon',
            'hotel',
            'order_number',
            'slug'
        )


class ServiceClientGetSerializer(serializers.ModelSerializer):
    hotel = serializers.CharField(source='hotel.user.username')

    class Meta:
        model = TechnicalService
        fields = (
            'id',
            'title',
            'icon',
            'hotel',
            'order_number',
            'slug'
        )


class ServiceUpdateDeleteSerialzier(serializers.ModelSerializer):
    class Meta:
        model = TechnicalService
        fields = (
            'title_az',
            'title_tr',
            'title_ar',
            'title_en',
            'title_ru',
            'title_ko',
            'icon',
            'order_number'
        )


class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalService
        fields = (
            'title_az',
            'title_tr',
            'title_ar',
            'title_en',
            'title_ru',
            'title_ko',
            'icon',
            'order_number'
        )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        service = TechnicalService.objects.create(**validated_data, hotel=user.hotel)
        return service


class RestaurantListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    profile_photo = serializers.ImageField(source='user.profile_photo')

    class Meta:
        model = Restaurant
        fields = (
            'username',
            'first_name',
            'last_name',
            'profile_photo',
            'slug'
        )


class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImages
        fields = ('image',)


class CustomerServiceCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )  # Manually handle multiple image uploads

    class Meta:
        model = Service
        fields = (
            'title_az', 'title_tr', 'title_ar', 'title_en', 'title_ru', 'title_ko',
            'photo', 'price', 'etp', 'description_az', 'description_tr',
            'description_ar', 'description_en', 'description_ru', 'description_ko',
            'images',  # Added field for multiple images
        )

    def create(self, validated_data):
        request = self.context['request']
        images = request.FILES.getlist('images')  # Get multiple images

        validated_data.pop('images', None)  # Remove 'images' to avoid TypeError

        user = request.user
        service = Service.objects.create(**validated_data, hotel=user.hotel)

        # Create ServiceImages for each uploaded image
        for image in images:
            ServiceImages.objects.create(service=service, image=image)

        return service


class CustomerServiceGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            'id',
            'title_az',
            'title_tr',
            'title_ar',
            'title_en',
            'title_ru',
            'title_ko',
            'photo',
            'price',
            'etp',
            'slug',
        )


class CustomerServiceClientGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            'id',
            'title',
            'photo',
            'price',
            'etp',
            'slug',
        )


class CustomerServiceDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = (
            'id',
            'title_az',
            'title_tr',
            'title_ar',
            'title_en',
            'title_ru',
            'title_ko',
            'photo',
            'description_az',
            'description_tr',
            'description_ar',
            'description_en',
            'description_ru',
            'description_ko',
            'price',
            'etp',
            'slug',
            'images'
        )

    def get_images(self, obj):
        """
        Returns a list of image URLs for the given service.
        """
        return [image.image.url for image in obj.serviceimages_set.all()]


class CustomerServiceClientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            'id',
            'title',
            'photo',
            'description',
            'price',
            'etp',
            'slug'
        )


class CustomerServiceUpdateSerialzier(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )

    class Meta:
        model = Service
        fields = (
            'title_az', 'title_tr', 'title_ar', 'title_en', 'title_ru', 'title_ko',
            'photo', 'price', 'etp', 'description_az', 'description_tr',
            'description_ar', 'description_en', 'description_ru', 'description_ko',
            'images',
        )

    def update(self, instance, validated_data):
        request = self.context['request']
        images = request.FILES.getlist('images')

        validated_data.pop('images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


        if images:
            instance.serviceimages_set.all().delete()
            for image in images:
                ServiceImages.objects.create(service=instance, image=image)
        return instance


class QuestionCreateAdminSerializer(serializers.ModelSerializer):
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
        hotel = self.context['request'].user.hotel
        question = Question.objects.create(**validated_data, hotel=hotel)
        return question


class QuestionGetSerializer(serializers.ModelSerializer):
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


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['question', 'rating']


class BulkFeedbackCreateSerializer(serializers.Serializer):
    description = serializers.CharField(allow_blank=True, required=False)
    overall_rating = serializers.IntegerField()
    room_id = serializers.CharField(required=False)
    feedbacks = FeedbackSerializer(many=True)

    def create(self, validated_data):
        feedbacks_data = validated_data.pop('feedbacks')
        room_id = validated_data.pop('room_id', None)
        if room_id:
            try:
                room = HotelRoom.objects.get(room_id=room_id)
                validated_data['room'] = room
            except HotelRoom.DoesNotExist:
                raise serializers.ValidationError(f"HotelRoom with room_id {room_id} does not exist.")

        feedback_description = FeedbackDescription.objects.create(**validated_data)
        feedbacks = []
        for feedback_data in feedbacks_data:
            feedback = Feedback.objects.create(
                description=feedback_description,
                **feedback_data
            )
            feedbacks.append(feedback)

        return {
            'feedback_description': feedback_description,
            'feedbacks': feedbacks
        }


class HotelRoomGetSerialzier(serializers.ModelSerializer):
    class Meta:
        model = HotelRoom
        fields = (
            'id',
            'room_id',
            'name'
        )


class HotelRoomCreateUpdateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = HotelRoom
        fields = (
            'name',
        )

    def create(self, validated_data):
        hotel = self.context['request'].user.hotel
        room = HotelRoom.objects.create(**validated_data, hotel=hotel)
        return room


class FeedbackListSerializer(serializers.ModelSerializer):
    room = serializers.CharField(source='room.name')

    class Meta:
        model = FeedbackDescription
        fields = (
            'id',
            'room',
            'description',
            'overall_rating',
            'created_at'
        )


class FeedbackAnswerListSerializer(serializers.ModelSerializer):
    room = serializers.CharField(source='description.room.name')
    description = serializers.CharField(source='description.description')
    created_at = serializers.DateTimeField(source='description.created_at')

    class Meta:
        model = Feedback
        fields = (
            'id',
            'room',
            'description',
            'rating',
            'created_at'
        )


class FeedbackInQuestionSerialzier(serializers.ModelSerializer):
    room = serializers.CharField(source='description.room.name')
    created_at = serializers.DateTimeField(source='description.created_at')

    class Meta:
        model = Feedback
        fields = (
            'id',
            'rating',
            'room',
            'created_at'
        )


class QuestionWithAnswersSerialzier(serializers.ModelSerializer):
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
        # Check if the filtered_feedbacks attribute exists
        if hasattr(obj, 'filtered_feedbacks'):
            return FeedbackInQuestionSerialzier(obj.filtered_feedbacks, many=True).data
        # Fallback to normal feedbacks if filtered_feedbacks is not present
        return FeedbackInQuestionSerialzier(obj.feedbacks, many=True).data


class FeedbackDescriptionStatisticSerializer(serializers.ModelSerializer):
    daily_feedbacks = serializers.SerializerMethodField()
    weekly_feedbacks = serializers.SerializerMethodField()
    monthly_feedbacks = serializers.SerializerMethodField()
    total_feedbacks = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackDescription
        fields = ('daily_feedbacks', 'weekly_feedbacks', 'monthly_feedbacks', 'total_feedbacks')

    def get_daily_feedbacks(self, obj):
        hotel = self.context['request'].user.hotel
        today = timezone.now().date()
        return FeedbackDescription.objects.filter(created_at__date=today, room__hotel=hotel).count()

    def get_weekly_feedbacks(self, obj):
        hotel = self.context['request'].user.hotel
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())
        week_end = week_start + timezone.timedelta(days=6)
        return FeedbackDescription.objects.filter(created_at__date__range=[week_start, week_end],
                                                  room__hotel=hotel).count()

    def get_monthly_feedbacks(self, obj):
        hotel = self.context['request'].user.hotel
        today = timezone.now().date()
        month_start = today.replace(day=1)
        month_end = today.replace(day=monthrange(today.year, today.month)[1])
        return FeedbackDescription.objects.filter(created_at__date__range=[month_start, month_end],
                                                  room__hotel=hotel).count()

    def get_total_feedbacks(self, obj):
        hotel = self.context['request'].user.hotel
        return FeedbackDescription.objects.filter(room__hotel=hotel).count()
