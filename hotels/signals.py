from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service, TechnicalService, HotelRoom
from django.utils.text import slugify
import uuid



@receiver(post_save, sender=Service)
def generate_service_slug(sender, instance, created, **kwargs):
    if created:
        slug = slugify(instance.title, allow_unicode=True)+uuid.uuid4().hex[:6].upper()
        instance.slug = slug
        instance.save()


@receiver(post_save, sender=TechnicalService)
def generate_service_slug(sender, instance, created, **kwargs):
    if created:
        slug = slugify(instance.title, allow_unicode=True)+uuid.uuid4().hex[:6].upper()
        instance.slug = slug
        instance.save()


@receiver(post_save, sender=HotelRoom)
def generate_service_slug(sender, instance, created, **kwargs):
    if created:
        room_id = instance.name+'-'+uuid.uuid4().hex[:6].upper()
        instance.room_id = room_id
        instance.save()