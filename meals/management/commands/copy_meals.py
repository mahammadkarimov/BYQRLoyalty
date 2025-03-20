from django.core.management.base import BaseCommand
from meals.models import Meal, Restaurant, MealCategory, SubCategory  # Düzgün app adını dəyişin


class Command(BaseCommand):
    help = "Copy meals and their categories from lovebar to premiumpark."

    def handle(self, *args, **kwargs):
        try:
            # Restoranları tap
            lovebar = Restaurant.objects.get(user__username="lovebar")
            premiumpark = Restaurant.objects.get(user__username="premiumpark")

            # Əsas kateqoriyaları tap və kopyala
            main_categories = [592, 593, 594]
            categories = MealCategory.objects.filter(id__in=main_categories, created_from=lovebar)

            category_mapping = {}
            for category in categories:
                new_category = MealCategory.objects.create(
                    created_from=premiumpark,
                    name=category.name,
                    icon=category.icon,
                    order=category.order,
                    is_active=category.is_active,
                )
                category_mapping[category.id] = new_category

            # Alt kateqoriyaları tap və kopyala
            subcategories = SubCategory.objects.filter(main_category__in=categories, created_from=lovebar)
            subcategory_mapping = {}
            for subcategory in subcategories:
                new_subcategory = SubCategory.objects.create(
                    created_from=premiumpark,
                    name=subcategory.name,
                    order=subcategory.order,
                    main_category=category_mapping[subcategory.main_category.id],
                    image=subcategory.image
                )
                subcategory_mapping[subcategory.id] = new_subcategory

            # Meals obyektlərini tap və kopyala
            meals_to_copy = Meal.objects.filter(category__in=subcategories, created_from=lovebar)
            for meal in meals_to_copy:
                meal.pk = None  # Yeni obyekt üçün PK silinir
                meal.created_from = premiumpark
                meal.category = subcategory_mapping[meal.category.id]
                meal.save()

            self.stdout.write(self.style.SUCCESS(
                f"Successfully copied {len(categories)} categories, {len(subcategories)} subcategories, and {meals_to_copy.count()} meals to premiumpark."))
        except Restaurant.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Restaurant not found: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
