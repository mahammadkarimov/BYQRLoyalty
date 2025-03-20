import uuid
from collections.abc import Iterable
import numpy as np
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image, ImageFilter
import blurhash
from base_user.models import Restaurant, Client

# import datetime

User = get_user_model()


# add category bolmesi olacaq. category name, category icon ve slug olacaq.
# editlene ve silinebilecek.

class MealCategory(models.Model):
    created_from = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    subcategories = models.ManyToManyField('SubCategory', blank=True)
    name = models.CharField(max_length=200, unique=False)
    icon = models.ImageField(upload_to="CatImages")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, allow_unicode=True)

    def __str__(self) -> str:
        return self.name + " - " + str(self.created_from)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True) + uuid.uuid4().hex[:6].upper()
        return super(MealCategory, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'


# add product bolmesi olacaq. product name, product image, productun terkibi,
# product price, vegan veya etyeyen olmasi (true veya false deyeri).

class SubCategory(models.Model):
    created_from = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, unique=False)
    order = models.IntegerField(default=0)
    main_category = models.ForeignKey('MealCategory', on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(null=True, blank=True, allow_unicode=True)
    image = models.ImageField(upload_to="sub_category_images",
                              null=True,
                              blank=True)

    def __str__(self) -> str:
        return self.name + " - " + str(self.created_from)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True) + uuid.uuid4().hex[:6].upper()
        return super(SubCategory, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Subcategories'
        verbose_name = 'Subcategory'


class Cousine(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Meal(models.Model):
    created_from = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='meals')
    name = models.CharField(null=True, blank=True, max_length=250, unique=False)
    image = models.ImageField(upload_to="mealImages", null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    number_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vegan = models.BooleanField(default=False)
    ingredient = models.TextField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=200)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_halal = models.BooleanField(default=False, null=True, blank=True)
    is_new = models.BooleanField(default=False, null=True, blank=True)
    etp = models.CharField(max_length=100, null=True, blank=True)
    calorie = models.PositiveIntegerField(null=True, blank=True)
    video = models.FileField(upload_to='meal_videos/', null=True, blank=True)
    cousine = models.ManyToManyField(Cousine, related_name='meals', null=True, blank=True)
    priority = models.IntegerField(default=0)

    iiko_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self) -> str:
        if self.name:
            return self.name
        return "Az dilisi yoxdur"

    def rating(self):
        result = self.reviews.aggregate(models.Avg('rating'))['rating_avg']
        return result or 0

    def get_discounted_price(self):
        if self.created_from and self.created_from.loyalty_discount_percent > 0 and self.number_price:
            discount = (self.created_from.loyalty_discount_percent / 100) * self.number_price
            return round(self.number_price - discount, 2)
        return self.number_price

    def save(self, *args, **kwargs):
        # Generate slug if it's not provided
        if not self.slug:
            self.slug = slugify(self.name) + uuid.uuid4().hex[:6].upper()

        # Process and compress the image if it's changed
        if self.image and hasattr(self.image, 'file') and hasattr(self.image.file, 'content_type'):
            content_type = self.image.file.content_type
            if 'image' in content_type:
                with Image.open(self.image) as pil_image:
                    # Convert image to RGB mode
                    pil_image = pil_image.convert('RGB')

                    # Resize the image using the LANCZOS filter (formerly ANTIALIAS)
                    output_size = (800, 800)  # adjust as necessary
                    pil_image.thumbnail(output_size, Image.LANCZOS)

                    # Convert image to a more efficient format (e.g., JPEG)
                    image_io = BytesIO()
                    pil_image.save(image_io, format='JPEG', quality=70,
                                   optimize=True)  # Adjust quality for a balance of size and quality

                    # Change the image field to the new compressed image
                    image_io.seek(0)
                    image_file = InMemoryUploadedFile(image_io, None, f'{self.slug}.jpg', 'image/jpeg', image_io.tell(),
                                                      None)
                    self.image = image_file

        super(Meal, self).save(*args, **kwargs)


class MealReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_reviews')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='reviews')
    comment = models.CharField(max_length=250, null=True, blank=True)
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user}"


class MealSize(models.Model):
    size = models.CharField(max_length=100, null=True, blank=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='sizes')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.meal}-{self.size}'

    def get_discounted_price(self):
        if self.meal.created_from and self.meal.created_from.loyalty_discount_percent > 0 and self.price:
            discount = (self.meal.created_from.loyalty_discount_percent / 100) * self.price
            return round(self.price - discount, 2)
        return self.price

    class Meta:
        ordering = ['price']


class MealImage(models.Model):
    image = models.ImageField(upload_to='meal_images')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.meal.name

    class Meta:
        ordering = ['-created_at']

    # def save(self, *args, **kwargs):
    #     # Print the ingredient - existing functionality
    #     print(self.ingredient)
    #
    #     # Generate and set the slug - existing functionality
    #     self.slug = slugify(self.name)
    #
    #     # Process the image for compression - new functionality
    #     if self.image:
    #         # Open the uploaded image
    #         pil_image = Image.open(self.image)
    #
    #         # Convert the image to RGB if it's not
    #         if pil_image.mode in ('RGBA', 'LA'):
    #             background = Image.new(pil_image.mode[:-1], pil_image.size, "#fff")
    #             background.paste(pil_image, pil_image.split()[-1])
    #             pil_image = background
    #
    #         # Resize/Process the image here (if needed)
    #         # pil_image = pil_image.resize((width, height))
    #
    #         # Save the processed image to a BytesIO object
    #         output_io = BytesIO()
    #         pil_image.save(output_io, format='JPEG', quality=70)  # Adjust quality as needed
    #
    #         # Change the ImageField to the new, processed image
    #         self.image.save(self.image.name, ContentFile(output_io.getvalue()), save=False)
    #
    #     # Call the "real" save method
    #     super(Meal, self).save(*args, **kwargs)
    #


class Basket(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='baskets')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.client} - {self.created_at}'


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    size = models.ForeignKey(MealSize, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.meal} - {self.quantity}'


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='orders')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.client} - {self.total_price}'

    def total_price(self):
        total = self.basket.items.aggregate(total_price=models.Sum('price'))['total_price']
        return total if total else 0


class FavoriteMeal(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='favorites')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.client} - {self.meal}'
