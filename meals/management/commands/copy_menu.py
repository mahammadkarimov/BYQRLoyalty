from typing import Any
from django.core.management.base import BaseCommand
from meals.models import Meal, MealCategory, SubCategory, MealImage, MealSize
from base_user.models import Restaurant
from decimal import Decimal


class Command(BaseCommand):
    help = 'Copy Menu'

    def handle(self, *args, **kwargs):
        restaurant = Restaurant.objects.get(user__username='urfasofrasi')
        new_restaurant = Restaurant.objects.get(user__username='urfasofrasibaku')
        print(new_restaurant)
        meals = Meal.objects.filter(created_from=restaurant)
        categories = MealCategory.objects.filter(created_from=restaurant)

        count = 1
        for category in categories:
            cat = MealCategory.objects.create(created_from=new_restaurant, name_az=category.name_az,
                                              name_ar=category.name_ar, name_ru=category.name_ru,
                                              name_en=category.name_en, name_ko=category.name_ko,
                                              name_tr=category.name_tr, icon=category.icon, order=category.order,
                                              is_active=category.is_active)
            print(count, cat)
            count += 1

            subcategories = SubCategory.objects.filter(created_from=restaurant, main_category=category)
            count_category = 1
            for subcategory in subcategories:
                subcat = SubCategory.objects.create(created_from=new_restaurant, name_az=subcategory.name_az,
                                                    name_ar=subcategory.name_ar, name_ru=subcategory.name_ru,
                                                    name_en=subcategory.name_en, name_ko=subcategory.name_ko,
                                                    name_tr=subcategory.name_tr, order=subcategory.order,
                                                    main_category=cat)
                print(" ", count_category, subcat)
                count_category += 1
                meals = Meal.objects.filter(created_from=restaurant, category=subcategory)
                count_meal = 1
                for meal in meals:
                    m = Meal.objects.create(
                        created_from=new_restaurant,
                        category=subcat,
                        name_az=meal.name_az,
                        name_ar=meal.name_ar,
                        name_tr=meal.name_tr,
                        name_ru=meal.name_ru,
                        name_en=meal.name_en,
                        name_ko=meal.name_ko,
                        image=meal.image,
                        price=meal.price,
                        number_price=meal.number_price,
                        vegan=meal.vegan,
                        ingredient_az=meal.ingredient_az,
                        ingredient_en=meal.ingredient_en,
                        ingredient_tr=meal.ingredient_tr,
                        ingredient_ru=meal.ingredient_tr,
                        ingredient_ko=meal.ingredient_ko,
                        ingredient_ar=meal.ingredient_ar,
                        is_active=meal.is_active,
                        is_halal=meal.is_halal,
                        is_new=meal.is_new,
                        etp=meal.etp,
                        calorie=meal.calorie,
                        video=meal.video
                    )
                    print("  ", count_meal, m)
                    count_meal += 1
                    mealsizes = MealSize.objects.filter(meal=meal)
                    count_size = 1
                    for mealsize in mealsizes:
                        msize = MealSize.objects.create(
                            size_az=mealsize.size_az,
                            size_ar=mealsize.size_ar,
                            size_en=mealsize.size_en,
                            size_tr=mealsize.size_tr,
                            size_ru=mealsize.size_ru,
                            size_ko=mealsize.size_ko,
                            meal=m,
                            price=mealsize.price
                        )
                        print("   ", count_size, msize)
                        count_size += 1
                    mealimages = MealImage.objects.filter(meal=meal)

                    count_image = 1
                    for mealimage in mealimages:
                        mimage = MealImage.objects.create(
                            image=mealimage.image,
                            meal=m
                        )
                        print("   ", count_image, mimage)
                        count_image += 1

        self.stdout.write(self.style.SUCCESS('All meals created!'))
