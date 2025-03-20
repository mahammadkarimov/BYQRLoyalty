from rest_framework import serializers
from .models import Table, TableCategory, Reservation, WaiterFeedback, PopularOffer
from datetime import datetime
from base_user.models import Waiter
from django.db.models import Avg
from base_user.serializers import RestaurantListSerialzier


class TableCategoryGetSeriazlizer(serializers.ModelSerializer):
    class Meta:
        model = TableCategory
        fields = (
            'id',
            'title'
        )


class TableGetSerializer(serializers.ModelSerializer):
    restaurant = serializers.CharField(source='restaurant.user.username')
    is_reserved = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            'id',
            'name',
            'table_id',
            'waiter',
            'is_available',
            'is_reserved',
            'restaurant'
        )

    def get_is_reserved(self, obj):
        try:
            waiter = self.context['request'].user.waiter
            if obj.current_waiter == waiter:
                return True
            return False
        except:
            return False


class WaiterInTableSerialzier(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    profile_photo = serializers.ImageField(source='user.profile_photo')
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Waiter
        fields = (
            'id',
            'waiter_id',
            'first_name',
            'last_name',
            'rating',
            'profile_photo'
        )

    def get_rating(self, obj):
        # obj here is an instance of Waiter
        average_rating = obj.feedbacks.aggregate(Avg('rate'))['rate__avg']
        return average_rating if average_rating is not None else 0.0


class TableDetailSerializer(serializers.ModelSerializer):
    restaurant = serializers.CharField(source='restaurant.user.username')
    is_reserved = serializers.SerializerMethodField()
    current_waiter = WaiterInTableSerialzier()

    class Meta:
        model = Table
        fields = (
            'id',
            'name',
            'table_id',
            'is_available',
            'is_reserved',
            'restaurant',
            'current_waiter'
        )

    def get_is_reserved(self, obj):
        try:
            waiter = self.context['request'].user.waiter
            if obj.current_waiter == waiter:
                return True
            return False
        except:
            return False


class ReservationCreateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            'table',
        )

    def validate(self, attrs):
        table = attrs.get('table')
        if table.is_available == False:
            raise serializers.ValidationError('This table has been already reserved!')
        return super().validate(attrs)

    def create(self, validated_data):
        waiter = self.context['request'].user.waiter
        print(waiter)
        reservation = Reservation.objects.create(**validated_data, waiter=waiter)
        return reservation


class ReservationEndSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            'end',
        )

    def update(self, instance, validated_data):
        instance.end = datetime.now()
        return super().update(instance, validated_data)


class TableCreateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = (
            'name',
            # 'category'
        )

    def create(self, validated_data):
        restaurant = self.context['request'].user.restaurant
        table = Table.objects.create(**validated_data, restaurant=restaurant)
        return table


class TableCreateHotelAdminSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = (
            'name',
            # 'category'
        )

    def create(self, validated_data):
        restaurant = self.context['restaurant']
        table = Table.objects.create(**validated_data, restaurant=restaurant)
        return table


class TableUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = (
            'name',
            # 'category'
        )


class WaiterFeedbackGetSeralizer(serializers.ModelSerializer):
    table = serializers.CharField(source='table.name')

    class Meta:
        model = WaiterFeedback
        fields = (
            'id',
            'get_waiter_id',
            'table',
            'created_at',
            'description',
            'rate'
        )


class WaiterFeedbackDetailSerialzier(serializers.ModelSerializer):
    class Meta:
        model = WaiterFeedback
        fields = (
            'rate',
            'description',
            'get_waiter_full_name',
            'get_waiter_id'
        )


class OfferSerializer(serializers.ModelSerializer):
    restaurant = RestaurantListSerialzier()

    class Meta:
        model = PopularOffer
        fields = "__all__"
