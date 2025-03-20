from django.core.management.base import BaseCommand
from meals.models import Meal, Restaurant  # Düzgün app adını dəyişin

class Command(BaseCommand):
    help = "Delete Meal objects with category__created_from = lovebar and created_from = premiumpark."

    def handle(self, *args, **kwargs):
        try:
            # Restoranları tap
            lovebar = Restaurant.objects.get(user__username="lovebar")
            premiumpark = Restaurant.objects.get(user__username="premiumpark")

            # Şərtlərə uyğun Meal obyektlərini tap və sil
            meals_to_delete = Meal.objects.filter(
                category__created_from=lovebar,
                created_from=premiumpark
            )
            count = meals_to_delete.count()
            meals_to_delete.delete()

            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} Meal objects."))
        except Restaurant.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Restaurant not found: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
