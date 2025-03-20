import django_filters
from django.db.models import Avg, Value, FloatField
from .models import Meal, Cousine
from django.db.models.functions import Coalesce

class MealFilter(django_filters.FilterSet):
    # Custom filters for rating
    min_rating = django_filters.NumberFilter(method='filter_by_min_rating', label='Min Rating')
    max_rating = django_filters.NumberFilter(method='filter_by_max_rating', label='Max Rating')
    
    # Filter meals by cousine IDs
    cousine = django_filters.ModelMultipleChoiceFilter(
        field_name='cousine',
        queryset=Cousine.objects.all(),
        to_field_name='id',  # Accept ID of Cousines
        label='Cousine IDs'
    )

    class Meta:
        model = Meal
        fields = ['cousine']

    def filter_by_min_rating(self, queryset, name, value):
        # Replace None with 0.0 for avg_rating (as Float) and filter by min rating
        return queryset.annotate(
            avg_rating=Coalesce(Avg('reviews__rating'), Value(0.0), output_field=FloatField())
        ).filter(avg_rating__gte=value)

    def filter_by_max_rating(self, queryset, name, value):
        # Replace None with 0.0 for avg_rating (as Float) and filter by max rating
        return queryset.annotate(
            avg_rating=Coalesce(Avg('reviews__rating'), Value(0.0), output_field=FloatField())
        ).filter(avg_rating__lte=value)
