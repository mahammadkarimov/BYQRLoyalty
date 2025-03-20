from django.dispatch import receiver
from django.db.models.signals import post_save
from PIL import Image, ImageFilter
from blurhash import encode
from .models import Meal


@receiver(post_save, sender=Meal)
def generate_blurred_image_and_blurhash(sender, instance, created, **kwargs):
    if created or instance.image != instance._old_image:
        with Image.open(instance.image.path) as img:
            blurred_img = img.filter(ImageFilter.GausiianBlur(radius=5)) # Blur the image
            blurred_img_path = f"blurredMealImages/{instance.image.name.split('/')[-1]}"
            blurred_img.save(blurred_img_path)

            # Generate blurhash for the blurred image
            blurhash = encode(blurred_img_path, x_components=4, y_components=3)

            # Update the model fields
            instance.blurred_image = blurred_img_path
            instance.blurhash = blurhash
            instance.save()