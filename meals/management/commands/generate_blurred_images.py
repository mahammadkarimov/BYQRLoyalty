import numpy as np
import base64
from django.core.management.base import BaseCommand
from PIL import Image, ImageFilter
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.text import slugify
from meals.models import Meal
import blurhash

class Command(BaseCommand):
    help = 'Generate blurred images and Base64 encoded versions for all Meal objects'

    def handle(self, *args, **kwargs):
        count = 1
        for meal in Meal.objects.all():
            print(count, meal)
            count += 1
            if meal.image:
                with Image.open(meal.image) as pil_image:
                    # Convert image to RGB mode
                    pil_image = pil_image.convert('RGB')

                    # Apply blur filter
                    blurred_img = pil_image.filter(ImageFilter.GaussianBlur(radius=50))

                    # Convert image to numpy array
                    img_array = np.array(blurred_img)

                    # Generate BlurHash for the blurred image
                    blur_hash = blurhash.encode(img_array, components_x=4, components_y=3)
                    meal.blurhash = blur_hash

                    # Save the blurred image to a BytesIO buffer
                    blurred_buffer = BytesIO()
                    blurred_img.save(blurred_buffer, format='JPEG')

                    # Encode the blurred image to Base64
                    blurred_base64 = base64.b64encode(blurred_buffer.getvalue()).decode('utf-8')

                    # Save the Base64 encoded string to the blurred_image_base64 field
                    meal.blurred_image_base64 = blurred_base64

                    # Create a ContentFile from the buffer
                    blurred_content = ContentFile(blurred_buffer.getvalue())

                    # Assign the blurred image to the blurred_image field
                    meal.blurred_image.save(f"{slugify(meal.name)}_blurred.jpg", blurred_content, save=False)

                    meal.save()

        self.stdout.write(self.style.SUCCESS('Successfully generated blurred images and Base64 encoded versions for all Meal objects'))
