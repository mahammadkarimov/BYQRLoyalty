from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Table, Reservation
from uuid import uuid4 


@receiver(post_save, sender = Table)
def generate_id(sender, instance, created, **kwargs):
    if created:
        id = str(uuid4())[:8]
        instance.table_id = id
        instance.save()


@receiver(pre_save, sender = Reservation)
def is_available(sender, instance, **kwargs):
    if instance.end is None:
        instance.table.is_available = False
        instance.table.current_waiter = instance.waiter
    else:
        instance.table.is_available = True
        instance.table.current_waiter = None

    instance.table.save()
