import json
from typing import Any
import requests
from io import BytesIO
from django.core.files import File
from django.core.management.base import BaseCommand
from meals.models import Meal, MealCategory, SubCategory, MealImage
from base_user.models import Restaurant
from decimal import Decimal
import os
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Copy Menu'

    def handle(self, *args, **kwargs):
        # Fetch the restaurant
        restaurant = Restaurant.objects.get(user__username='plove')
        print(restaurant)

        # Open and read the JSON file
        with open("plov.json", 'r') as file:
            menu = json.load(file)  # Read and parse the JSON data as a dictionary
        order = 1
        for i in menu.items():
            category = MealCategory.objects.get(name=i[1]["parent"], created_from=restaurant)
            if not SubCategory.objects.filter(name_az=i[1]["category_az"], created_from=restaurant).exists():
                subcategory = SubCategory.objects.create(
                    created_from=restaurant, 
                    main_category=category, 
                    order=order, 
                    name_az=i[1]["category_az"], 
                    name_ru=i[1]["category_ru"], 
                    name_en=i[1]["category_en"]
                )
            else:
                subcategory = SubCategory.objects.get(
                    created_from=restaurant, 
                    name_az=i[1]["category_az"]
                )
            print(subcategory)
            
            order += 1

            for meal in i[1]["meals"]:
                # Check if the meal already exists, otherwise create it
                if not Meal.objects.filter(
                    created_from=restaurant, 
                    category=subcategory, 
                    name_az=meal["name_az"]
                ).exists():
                    m = Meal.objects.create(
                        created_from=restaurant, 
                        category=subcategory, 
                        name_az=meal["name_az"], 
                        name_ru=meal["name_ru"], 
                        name_en=meal["name_en"], 
                        price=meal["price"], 
                        number_price=Decimal(meal["price"]), 
                        ingredient_az=meal["description_az"], 
                        ingredient_ru=meal["description_ru"], 
                        ingredient_en=meal["description_en"]
                    )
                    
                    # Handle image download or default image
                    image_url = meal.get("image")
                    print(image_url)
                    if image_url:
                        try:
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                            }
                            response = requests.get(image_url, headers=headers, timeout=10)
                            if response.status_code == 200 and 'image' in response.headers['Content-Type']:
                                # Save the image in MealImage model
                                image_name = image_url.split('/')[-1]  # Extract the image file name
                                img_temp = BytesIO(response.content)  # Create a temporary in-memory file
                                meal_image = MealImage.objects.create(meal=m)  # Create MealImage instance
                                meal_image.image.save(image_name, File(img_temp), save=True) 
                                m.image.save(image_name, File(img_temp), save=True)
                            else:
                                print(f"Failed to download image for {meal['name_az']}, using default image.")
                                self.assign_default_image(m)
                        except requests.exceptions.RequestException as e:
                            print(f"Error downloading image for {meal['name_az']}: {e}")
                            self.assign_default_image(m)
                    else:
                        print(f"No image URL provided for {meal['name_az']}, using default image.")
                        self.assign_default_image(m)

                    # Add a small delay to prevent rate-limiting
                    time.sleep(2)

                else:
                    m = Meal.objects.get(created_from=restaurant, category=subcategory, name_az=meal["name_az"])
                
                print(m)

        self.stdout.write(self.style.SUCCESS('All meals created!'))

    def assign_default_image(self, meal):
        """Assign a default image to the meal when no image is provided or download fails."""
        default_image_path = os.path.join(settings.MEDIA_ROOT, 'default_food.jpeg')
        if os.path.exists(default_image_path):
            with open(default_image_path, 'rb') as default_image:
                meal_image = MealImage.objects.create(meal=meal)
                meal_image.image.save('default_food.jpg', File(default_image), save=True)
                meal.image = meal_image.image  # Assign the saved image to meal.image
                meal.save()
        else:
            print(f"Default image not found at {default_image_path}")
