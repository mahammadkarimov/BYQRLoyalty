from typing import Iterable
from django.db import models
from base_user.models import Restaurant, Waiter


# Create your models here.


class TableCategory(models.Model):
    title = models.CharField(max_length=50)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='table_categories')

    def __str__(self):
        return f'{self.title} - {self.restaurant}'

    class Meta:
        verbose_name_plural = 'Table Categories'


class Table(models.Model):
    name = models.CharField(max_length=30)
    table_id = models.CharField(max_length=15, null=True, blank=True)
    category = models.ForeignKey(TableCategory, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='category_tables')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_tables')
    is_available = models.BooleanField(default=True)
    current_waiter = models.ForeignKey(Waiter, null=True, blank=True, on_delete=models.CASCADE, related_name='tables')
    iiko_id = models.CharField(max_length=150,
                               null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name} - {self.restaurant}'

    def waiter(self):
        if self.current_waiter is not None:
            return f'{self.current_waiter.user.first_name} {self.current_waiter.user.last_name}'
        return None

    class Meta:
        ordering = ['name']


class Reservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='table_reservations')
    waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE, related_name='waiter_reservations')
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.end is not None:
            self.is_active = False
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.table} - {self.waiter}'


class WaiterFeedback(models.Model):
    waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE, related_name='feedbacks')
    rate = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='waiter_feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.waiter} {self.rate}'

    def get_waiter_full_name(self):
        return f'{self.waiter.user.first_name} {self.waiter.user.last_name}'

    def get_waiter_id(self):
        print("balance:", self.waiter.balance)
        return str(self.waiter.waiter_id)


class PopularOffer(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    image = models.ImageField(upload_to="offers/")

    def __str__(self):
        return self.restaurant.user.username

    class Meta:
        verbose_name = "Popular offer"
        verbose_name_plural = "Popular offers"

