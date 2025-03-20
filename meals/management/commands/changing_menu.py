from django.core.management.base import BaseCommand
from meals.models import SubCategory, Restaurant, Meal


class Command(BaseCommand):
    help = 'Update MealCategory objects created_from to lovebar restaurant'

    def handle(self, *args, **kwargs):
        try:
            lovebar_restaurant = Restaurant.objects.filter(user__username="lovebar").first()

            if not lovebar_restaurant:
                self.stdout.write(self.style.ERROR("No restaurant found with user 'lovebar'"))
                return

            updated_count = Meal.objects.filter(
                category__created_from__user__username="lovebar"
            ).update(created_from=lovebar_restaurant)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully updated {updated_count} SubCategory objects to 'lovebar' restaurant"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error occurred: {e}"))
