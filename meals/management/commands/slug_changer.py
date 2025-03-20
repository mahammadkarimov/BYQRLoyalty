from django.core.management.base import BaseCommand
from meals.models import Meal
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Make slugs unique for meals by appending numbers to duplicates'

    def handle(self, *args, **kwargs):
        # Tüm meal'leri al
        meals = Meal.objects.all()

        # Slug'ları kontrol etmek için bir dictionary oluştur
        slug_dict = {}

        for meal in meals:
            original_slug = meal.slug

            # Eğer bu slug daha önce eklenmişse
            if original_slug in slug_dict:
                # Sayıyı artırarak yeni bir slug oluştur
                slug_dict[original_slug] += 1
                new_slug = f"{original_slug}-{slug_dict[original_slug]}"
            else:
                # İlk defa görülen slug, sayıyı 0 olarak başlat
                slug_dict[original_slug] = 0
                new_slug = original_slug

            # Meal'in slug'ını güncelle
            if meal.slug != new_slug:
                meal.slug = new_slug
                meal.save()

                self.stdout.write(self.style.SUCCESS(f"Slug updated for meal '{meal.name}' to '{new_slug}'"))
            else:
                self.stdout.write(self.style.SUCCESS(f"No change needed for meal '{meal.name}'"))
