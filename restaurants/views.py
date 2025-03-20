from django.shortcuts import render
from .models import Table, TableCategory, Reservation, WaiterFeedback, PopularOffer
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from base_user.models import Restaurant
from django.utils import timezone
from datetime import datetime
from calendar import monthrange
from .serializers import (
    ReservationCreateSerialzier,
    ReservationEndSerialzier,
    TableGetSerializer,
    TableCategoryGetSeriazlizer,
    TableCreateSerialzier,
    TableUpdateSerializer,
    TableCreateHotelAdminSerialzier,
    TableDetailSerializer,
    WaiterFeedbackGetSeralizer,
    WaiterFeedbackDetailSerialzier, OfferSerializer)

# Create your views here.

class TableCategoryListView(ListAPIView):
    serializer_class = TableCategoryGetSeriazlizer
    queryset = TableCategory.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.waiter.restaurant
        queryset = TableCategory.objects.filter(restaurant=restaurant)
        return queryset


class TableRetrieveByNAmeView(RetrieveAPIView):
    serializer_class = TableDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        username = self.kwargs.get('username')
        name = self.kwargs.get('table_name')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        table = get_object_or_404(Table, restaurant=restaurant, name=name)
        return table


class TableListView(ListAPIView):
    serializer_class = TableGetSerializer
    queryset = Table.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.waiter.restaurant
        queryset = Table.objects.filter(restaurant=restaurant)
        return queryset


class TableHotelAdminListCreateView(ListCreateAPIView):
    serializer_class = TableGetSerializer
    queryset = Table.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username = username)
        queryset = Table.objects.filter(restaurant=restaurant)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TableCreateHotelAdminSerialzier
        return super().get_serializer_class()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        username = self.kwargs.get('username')
        restaurant = get_object_or_404(Restaurant, user__username=username)
        context['restaurant'] = restaurant
        return context


class TableHotelAdminRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = TableUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs.get(slug)
        table = get_object_or_404(Table, slug=slug)
        return table
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TableGetSerializer
        return super().get_serializer_class()


class MyReservedTablesView(ListAPIView):
    serializer_class = TableGetSerializer
    queryset = Table.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        waiter = self.request.user.waiter
        queryset = waiter.tables.all()
        return queryset


class ReservationCreateView(CreateAPIView):
    serializer_class = ReservationCreateSerialzier
    permission_classes = [IsAuthenticated]


class ReservationEndView(UpdateAPIView):
    serializer_class = ReservationEndSerialzier
    permission_classes = [IsAuthenticated]

    def get_object(self):
        table_id = self.kwargs.get('table_id')
        reservation = get_object_or_404(Reservation, table__id = table_id, is_active = True)
        print(reservation)
        return reservation
    

class TableCreateAdminView(CreateAPIView):
    serializer_class = TableCreateSerialzier
    permission_classes = [IsAuthenticated]


class TableCategoriesGetAdminView(ListAPIView):
    serializer_class = TableCategoryGetSeriazlizer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.restaurant
        quesryset = TableCategory.objects.filter(restaurant=restaurant)
        return quesryset
    

class TableListAdminView(ListAPIView):
    serializer_class = TableGetSerializer
    queryset = Table.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.restaurant
        queryset = restaurant.restaurant_tables.all()
        return queryset


class TableUpdateAdminView(UpdateAPIView):
    serializer_class = TableUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('table_id')
        table = get_object_or_404(Table, id=id)
        return table
    

class TableDeleteAdminView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('table_id')
        table = get_object_or_404(Table, id=id)
        return table


class TableRetrieveView(RetrieveAPIView):
    serializer_class = TableGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('table_id')
        table = get_object_or_404(Table, id=id)
        return table


class WaiterFeedbackListView(ListAPIView):
    serializer_class = WaiterFeedbackGetSeralizer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = self.request.user.restaurant
        queryset = WaiterFeedback.objects.filter(table__restaurant=restaurant)
        time = self.request.GET.get('time')
        today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        if time == 'today':
            queryset = WaiterFeedback.objects.filter(table__restaurant=restaurant, created_at__date=today.date())
        elif time == 'week':
            week_start = today - timezone.timedelta(days=today.weekday())
            week_end = week_start + timezone.timedelta(days=6, hours=23, minutes=59, seconds=59)
            queryset = WaiterFeedback.objects.filter(table__restaurant=restaurant, created_at__range=[week_start, week_end]) 
        elif time == 'month':
            month_start = today.replace(day=1)
            last_day = monthrange(today.year, today.month)[1]
            month_end = today.replace(day=last_day, hour=23, minute=59, second=59)
            queryset = WaiterFeedback.objects.filter(table__restaurant=restaurant, created_at__range=[month_start, month_end])
        return queryset
    

class WaiterFeedbackDetailView(RetrieveAPIView):
    serializer_class = WaiterFeedbackDetailSerialzier
    permission_classes = [IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get('id')
        feedback = get_object_or_404(WaiterFeedback, id=id)
        return feedback


class PopularOffersView(ListAPIView):
    queryset = PopularOffer.objects.all()
    serializer_class = OfferSerializer
