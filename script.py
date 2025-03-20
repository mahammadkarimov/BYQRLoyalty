import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byqr.settings') # Replace with your project's settings module
django.setup()

from meals.models import MealCategory, SubCategory, Restaurant

def transfer_and_delete_mealcategory():
    for meal_category in MealCategory.objects.all():
        # Create or get the SubCategory
        subcategory, created = SubCategory.objects.get_or_create(
            name=meal_category.name,
            defaults={
                'created_from': meal_category.created_from,
                'main_category': meal_category,
                'order': meal_category.order
            }
        )

        # If the subcategory is newly created, it won't have a slug, so we save it to generate one
        if created:
            subcategory.save()

        # Optionally, associate the new subcategory with the meal category
        # meal_category.subcategories.add(subcategory)
        # meal_category.save()

        print(f"{'Created' if created else 'Found'} subcategory '{subcategory.name}' for meal category '{meal_category.name}'")

        # Delete the meal_category after successful transfer
        meal_category.delete()
        print(f"Deleted meal category '{meal_category.name}' after transfer.")

# Run the function
transfer_and_delete_mealcategory()
