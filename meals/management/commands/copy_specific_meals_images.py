from django.core.management.base import BaseCommand
from meals.models import Meal, MealImage
from base_user.models import Restaurant


class Command(BaseCommand):
    help = 'Create MealImage instances for PremiumPark meals based on LobbyBar meals'

    def handle(self, *args, **kwargs):

        lobbybar = Restaurant.objects.filter(user__username='lobbybar').first()
        premiumpark = Restaurant.objects.filter(user__username='premiumpark').first()

        if not lobbybar or not premiumpark:
            self.stdout.write(self.style.ERROR('One or both of the restaurants not found.'))
            return


        lobbybar_meals = Meal.objects.filter(created_from=lobbybar)
        premiumpark_meals = Meal.objects.filter(created_from=premiumpark)

        for lobbybar_meal in lobbybar_meals:

            matching_meal = premiumpark_meals.filter(name=lobbybar_meal.name).first()

            if matching_meal:

                for image in lobbybar_meal.images.all():
                    MealImage.objects.create(meal=matching_meal, image=image.image)

                self.stdout.write(self.style.SUCCESS(f'Created MealImage for {matching_meal.name}'))

        self.stdout.write(self.style.SUCCESS('Command completed successfully'))
