from django.core.management.base import BaseCommand
from meals.models import Meal
from meals.models import MealImage
from django.db import transaction


class Command(BaseCommand):
    help = 'Sync MealImages from lobbybar meals to premiumpark meals based on slug matches'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting the sync process...")

        # Lobbybar və Premiumpark meal-larını götürürük
        lobby_meals = Meal.objects.filter(created_from__slug="pirosmaniAE748D")
        self.stdout.write(f"Sync process completed. Total synced meals: {lobby_meals}")
        premium_meals = Meal.objects.filter(created_from__slug="premiumpark663347")

        synced_count = 0

        with transaction.atomic():
            for lobby_meal in lobby_meals:
                self.stdout.write(lobby_meal.slug)
                # Premiumpark-da uyğun slug olan məhsulu tapırıq
                premium_meal = premium_meals.filter(slug__icontains=lobby_meal.slug).first()
                # self.stdout.write(premium_meal)
                if premium_meal:
                    # Lobbybar məhsulunun şəkillərini götürürük
                    if lobby_meal.image:
                        # Əgər şəkil varsa, onu yeni MealImage obyektinə əlavə edirik
                        MealImage.objects.create(
                            image=lobby_meal.image,
                            meal=premium_meal
                        )
                        synced_count += 1
                        self.stdout.write(
                            f"Synced image from LobbyMeal '{lobby_meal.name}' to PremiumMeal '{premium_meal.name}'")

        self.stdout.write(f"Sync process completed. Total synced meals: {synced_count}")
