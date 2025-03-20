from django.db import models
from base_user.models import Hotel
from django.utils.text import slugify
import uuid


# Create your models here.

class TechnicalService(models.Model):
    title = models.CharField(max_length=250)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='technical_services')
    icon = models.ImageField(upload_to='tech_service_icons', null=True, blank=True)
    order_number = models.PositiveSmallIntegerField()
    slug = models.SlugField(null=True, blank=True)

    def __str__(self) -> str:
        return self.title


class Service(models.Model):
    title = models.CharField(max_length=250)
    photo = models.ImageField(upload_to='services_photo/', null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    description = models.TextField(null=True, blank=True)
    hotel = models.ForeignKey(Hotel, null=True, blank=True, on_delete=models.CASCADE, related_name='hotel_services')
    slug = models.SlugField(null=True, blank=True, allow_unicode=True)
    etp = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self) -> str:
        return self.title


class ServiceImages(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    image = models.FileField(upload_to="service_images/")

    def __str__(self):
        return self.service.title

    class Meta:
        verbose_name = "Service Image"
        verbose_name_plural = "Service Images"


class HotelRoom(models.Model):
    name = models.CharField(max_length=100)
    room_id = models.CharField(max_length=30, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self) -> str:
        return f'{self.name} - {self.hotel}'


class Question(models.Model):
    question = models.TextField()
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.question


class FeedbackDescription(models.Model):
    description = models.TextField(null=True, blank=True)
    overall_rating = models.PositiveSmallIntegerField()
    room = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.description


class Feedback(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveSmallIntegerField()
    description = models.ForeignKey(FeedbackDescription, blank=True, null=True, related_name='feedback_description',
                                    on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.question} - {self.rating}'
