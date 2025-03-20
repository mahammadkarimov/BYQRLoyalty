from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MyUser, Waiter, Client
from uuid import uuid4
import random
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile


def generate_card_id():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])


@receiver(post_save, sender=Waiter)
def generate_id(sender, instance, created, **kwargs):
    if created:
        id = str(uuid4())[:6]
        instance.waiter_id = id
        instance.save()


@receiver(post_save, sender=Client)
def generate_card_id_and_barcode(sender, instance, created, **kwargs):
    if instance.user.user_type == "loyal":
        if created:
            if not instance.card_id:
                instance.card_id = generate_card_id()

            barcode_object = barcode.get_barcode_class('code128')(instance.card_id, writer=ImageWriter())

            buffer = BytesIO()
            barcode_object.write(buffer)
            buffer.seek(0)

            file_name = f"{instance.card_id}.png"
            instance.barcode_image.save(file_name, ContentFile(buffer.read()), save=False)
            instance.save()
