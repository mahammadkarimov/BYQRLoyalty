from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Payment
import uuid


@receiver(post_save, sender=Payment)
def generate_order_id(sender, instance, created, **kwargs):
    if created:
        instance.order_id = str(uuid.uuid4()).upper()
        instance.save()
