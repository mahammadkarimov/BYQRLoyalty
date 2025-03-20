import django_filters
from .models import RestaurantSubCategory, Restaurant


class RestaurantSubCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = RestaurantSubCategory
        fields = ("parent",)

class RestaurantFilter(django_filters.FilterSet):
    class Meta:
        model = Restaurant
        fields = (
            "loyalty_discount_percent",
        )