from typing import Any
from django.core.management.base import BaseCommand
from meals.models import Meal
from decimal import Decimal

class Command(BaseCommand):
    help = 'Define decimal price for all meals'

    def handle(self, *args, **kwargs):
        meals = Meal.objects.all()
        count = 1
        fail = 0
        for meal in meals:
            try:
                meal.number_price = Decimal(meal.price)
                meal.save()
            except:
                print(meal.price, 'failed')
                fail += 1
            print(f"{count} - {meal.created_from.user.username} {meal.name} {meal.number_price}")
            count += 1
        print(f"{count} meals iterated, {fail} failed")
        self.stdout.write(self.style.SUCCESS('All slugs have been updated successfully!'))