from typing import Any
from django.core.management.base import BaseCommand
from meals.models import Meal
from django.utils.text import slugify
import uuid

class Command(BaseCommand):
    help = 'Regenerate slugs without unicode characters'

    def handle(self, *args, **kwargs):
        meals = Meal.objects.all()
        count = 1
        for meal in meals:
            slug = slugify(meal.name) + uuid.uuid4().hex[:6].upper()
            meal.slug = slug
            meal.save()
            print(f"{count} - {meal.created_from.user.username} {meal.name} {meal.slug}")
            count += 1

        self.stdout.write(self.style.SUCCESS('All slugs have been updated successfully!'))