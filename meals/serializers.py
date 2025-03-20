from collections import defaultdict
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.utils.translation import activate
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from collections import defaultdict
from rest_framework import serializers
from base_user.models import Restaurant, RestaurantPackage, Feature, Url, RetaurantLanguage, Currency, \
    RestaurantCampaign, RestaurantWorkingHour
from django.core.exceptions import ValidationError
import json
from decimal import Decimal
from django.shortcuts import get_object_or_404
from .models import MealCategory, Meal, SubCategory, MealImage, MealSize, Basket, BasketItem, Order, FavoriteMeal
from byqr.settings import CDN_BASE_URL


class CurrencySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='currency.name')
    symbol = serializers.CharField(source='currency.symbol')
    language = serializers.CharField(source='language.name')

    class Meta:
        model = Currency
        fields = (
            'id',
            'name',
            'symbol',
            'language'
        )


class MealImageSeriazlier(serializers.ModelSerializer):
    class Meta:
        model = MealImage
        fields = (
            'id',
            'image'
        )

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Fallback if request is not available
                return f"{obj.image.url}"
        else:
            return None


class MealSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealSize
        fields = ('id', 'size_az', 'size_en', 'size_ru', 'size_ko', 'size_tr', 'size_ar', 'price')
        extra_kwargs = {
            'id': {'read_only': True}
        }


class MealSizeInMealSerialzier(serializers.ModelSerializer):
    class Meta:
        model = MealSize
        fields = (
            'id',
            'size',
            'price'
        )


class RelatedMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ("id", "name", "price", "image", "slug")


class MealSerializer(serializers.ModelSerializer):
    category = serializers.SlugField(write_only=True, required=False, allow_unicode=True)
    images = MealImageSeriazlier(many=True, read_only=True)
    sizes = MealSizeInMealSerialzier(many=True)
    currency = CurrencySerializer(many=True, source='created_from.currency', read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    related_meals = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Meal
        fields = (
            "id", "name", "currency", "category", "name", "price", 'sizes', "image", "vegan", "ingredient", "is_active",
            "is_halal", "is_new", "etp", "slug", "is_favorite", "calorie", "video", "images", "iiko_id",
            "related_meals")
        # extra_kwargs = {'category': {'required': True}}

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Fallback if request is not available
                return f"{obj.image.url}"
        else:
            return None

    def get_video(self, obj):
        if obj.video and hasattr(obj.video, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.video.url)
            else:
                # Fallback if request is not available
                return f"{obj.video.url}"
        else:
            return None

    def get_is_favorite(self, obj):
        if self.context['request'].user.is_authenticated:
            client = self.context['request'].user.client
            is_favorite = True if FavoriteMeal.objects.filter(client=client, meal=obj).exists() else False
        else:
            is_favorite = False
        return is_favorite

    def update(self, instance, validated_data):
        # Handle category update
        category_slug = validated_data.pop('category', None)
        if category_slug:
            category, created = SubCategory.objects.get_or_create(slug=category_slug)
            instance.category = category

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):

        validated_data["created_from"] = self.context["request"].user.restaurant

        return super().create(validated_data)

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):

            return f"{obj.image.url}"
        else:
            return None

    def get_related_meals(self, obj):
        related_meals = Meal.objects.filter(category=obj.category).exclude(id=obj.id)[:10]
        return RelatedMealSerializer(related_meals, many=True, context=self.context).data


class FavoriteMealSerialzier(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)

    class Meta:
        model = FavoriteMeal
        fields = (
            'id',
            'meal'
        )


class MealAdminSerializer(serializers.ModelSerializer):
    category = serializers.SlugField(write_only=True, required=False, allow_unicode=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = MealImageSeriazlier(many=True, read_only=True)
    sizes = MealSizeSerializer(many=True, required=False)

    class Meta:
        model = Meal
        fields = (
            "name_az", "name_tr", "name_ar", "name_en", "name_ru", "name_ko", "category_name", "category", "price",
            "image", "images", "video", "vegan", "ingredient_az", "ingredient_tr", "ingredient_ar", "ingredient_en",
            "ingredient_ru", "ingredient_ko", "calorie", "is_active", "is_halal", "is_new", "etp", "sizes",
            "slug", "priority", "iiko_id")
        # extra_kwargs = {'category': {'required': True}}

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Fallback if request is not available
                return f"{obj.image.url}"
        else:
            return None

    def update(self, instance, validated_data):
        # Handle category update
        category_slug = validated_data.pop('category', None)
        if category_slug:
            category, created = SubCategory.objects.get_or_create(slug=category_slug)
            instance.category = category

        # Handle sizes update
        sizes_data = validated_data.pop('sizes', None)
        if sizes_data:
            existing_ids = [size.id for size in instance.sizes.all()]
            updated_ids = [item.get('id') for item in sizes_data if item.get('id')]

            # Delete sizes not in the updated data
            for size in instance.sizes.all():
                if size.id not in updated_ids:
                    size.delete()

            # Update or create sizes
            for size_data in sizes_data:
                size_id = size_data.get('id')
                if size_id and size_id in existing_ids:
                    size_instance = MealSize.objects.get(id=size_id, meal=instance)
                    size_instance.size = size_data.get('size', size_instance.size)
                    size_instance.price = size_data.get('price', size_instance.price)
                    size_instance.save()
                else:
                    MealSize.objects.create(meal=instance, **size_data)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):

        validated_data["created_from"] = self.context["request"].user.restaurant

        return super().create(validated_data)

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):

            return f"{obj.image.url}"
        else:
            return None


class MealSizeInMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealSize
        fields = ('size', 'price')


class CreateMealSerializer(serializers.ModelSerializer):
    category = serializers.CharField(write_only=True)  # Add a new field for category name
    images = MealImageSeriazlier(many=True, read_only=True)
    sizes = MealSizeInMealSerializer(read_only=True, many=True)
    created_sizes = serializers.CharField(write_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Meal
        fields = (
            "name_az", "name_tr", "name_ar", "name_en", "name_ru", "name_ko", "category", "price", "image", "images",
            "vegan", "is_active", "is_halal", "is_new", "ingredient_az", "ingredient_tr", "ingredient_ar",
            "ingredient_en",
            "ingredient_ru", "ingredient_ko", "etp", "calorie", "video", "uploaded_images", "created_sizes", "sizes",
            "iiko_id")

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        sizes_data = validated_data.pop("created_sizes", "[]")
        category_name = validated_data.pop("category")
        user = self.context["request"].user

        try:
            sizes_data = json.loads(sizes_data)
        except json.JSONDecodeError as e:
            raise ValidationError("Invalid JSON format for sizes")

        category, created = SubCategory.objects.get_or_create(created_from=user.restaurant, name=category_name)
        validated_data["category"] = category
        validated_data["created_from"] = self.context["request"].user.restaurant
        meal = Meal.objects.create(**validated_data)

        for size_data in sizes_data:
            print(f"Creating size: {size_data}")  # Debug print
            MealSize.objects.create(meal=meal, **size_data)

        for image in uploaded_images:
            MealImage.objects.create(meal=meal, image=image)

        return meal


class CreateMealHotelAdminSerializer(serializers.ModelSerializer):
    category = serializers.CharField(write_only=True)  # Add a new field for category name
    images = MealImageSeriazlier(many=True, read_only=True)
    sizes = MealSizeInMealSerializer(read_only=True, many=True)
    created_sizes = serializers.CharField(write_only=True, required=False)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Meal
        fields = (
            "name_az", "name_tr", "name_ar", "name_en", "name_ru", "name_ko", "category", "price", "image", "images",
            "vegan", "is_active", "is_halal", "is_new", "ingredient_az", "ingredient_tr", "ingredient_ar",
            "ingredient_en",
            "ingredient_ru", "ingredient_ko", "calorie", "etp", "video", "uploaded_images", "created_sizes", "sizes",
            "priority", "iiko_id")

    def validate(self, data):
        # Replace name_az with name_en if name_az is missing or empty
        if (data.get('name_az') is None or data.get('name_az') == '') and data.get('name_en'):
            data['name_az'] = data['name_en']

        # Replace ingredient_az with ingredient_en if ingredient_az is missing or empty
        if (data.get('ingredient_az') is None or data.get('ingredient_az') == '') and data.get('ingredient_en'):
            data['ingredient_az'] = data['ingredient_en']

        return data

    def create(self, validated_data):
        name_az = validated_data.get('name_az')
        ingredient_az = validated_data.get('ingredient_az')
        name_en = validated_data.get('name_en')
        ingredient_en = validated_data.get('ingredient_en')
        uploaded_images = validated_data.pop("uploaded_images", [])
        sizes_data = validated_data.pop("created_sizes", "[]")
        category_name = validated_data.pop("category")
        user = self.context["request"].user

        try:
            sizes_data = json.loads(sizes_data)
        except json.JSONDecodeError as e:
            raise ValidationError("Invalid JSON format for sizes")

        category, created = SubCategory.objects.get_or_create(created_from=user.restaurant, name=category_name)
        validated_data["category"] = category
        validated_data["created_from"] = self.context["request"].user.restaurant
        try:
            price = validated_data.get("price", 0)
            price = 0 if price == "" else Decimal(price)
            validated_data["number_price"] = price
        except:
            raise serializers.ValidationError({"message": "price should be decimal"})

        meal = Meal.objects.create(**validated_data)

        for size_data in sizes_data:
            price = size_data.get('price', 0)
            price = 0 if price == "" else Decimal(price)
            size_data.pop('price')
            MealSize.objects.create(meal=meal, **size_data, price=price)

        for image in uploaded_images:
            MealImage.objects.create(meal=meal, image=image)

        return meal


class MealImagesUpdateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = MealImage
        fields = (
            'image',
        )


class MealImageCreateSerialzier(serializers.ModelSerializer):
    meal_slug = serializers.CharField(write_only=True)

    class Meta:
        model = MealImage
        fields = (
            'image',
            'meal_slug'
        )

    def validate(self, attrs):
        slug = attrs.pop('meal_slug')
        meal = get_object_or_404(Meal, slug=slug)
        attrs['meal'] = meal
        return super().validate(attrs)


class MealVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = (
            'video',
        )


class GetSubCategorySerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = SubCategory
        fields = ("id", "name", "meals", "slug", "order")
        read_only_fields = ('id',)


class GetSubCategoryClientSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = SubCategory
        fields = ("id", "name", "meals", "slug", "order")
        read_only_fields = ('id',)


class SimpleGetSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ("id", "name_az", "name_tr", "name_en", "name_ko", "name_ru", "name_ar", "slug", "order", "image")
        read_only_fields = ('id',)


class MealCategorySerializer(serializers.ModelSerializer):
    subcategories = GetSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MealCategory
        fields = ("id", "name", "icon", "order", "subcategories", "slug")
        read_only_fields = ('id',)

    def create(self, validated_data):
        validated_data["created_from"] = self.context["request"].user.restaurant
        return super().create(validated_data)


class MealCategoryHotelAdminSerializer(serializers.ModelSerializer):
    subcategories = GetSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MealCategory
        fields = ("id", "name_az", "name_tr", "name_ar", "name_en", "name_ru", "name_ko", "icon", "order", "is_active",
                  "subcategories", "slug")
        read_only_fields = ('id',)
        extra_kwargs = {'icon': {'required': False}}

    def validate(self, data):
        if (data.get('name_az') is None or data.get('name_az') == '') and data.get('name_en'):
            data['name_az'] = data['name_en']
        return data

    def create(self, validated_data):
        return super().create(validated_data)


class GetMealCategorySerializer(serializers.ModelSerializer):
    subcategories = SimpleGetSubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = MealCategory
        fields = ("id", "name", "icon", "is_active", "order", "subcategories", "slug")
        read_only_fields = ('id',)


class SubCategorySerializer(serializers.ModelSerializer):
    main_category = MealCategorySerializer(read_only=True)  # If main_category is a foreign key
    main_category_slug = serializers.SlugField(write_only=True, required=False, allow_unicode=True,
                                               source='main_category')  # For write operations

    class Meta:
        model = SubCategory
        fields = ("id", "name", "order", "main_category", "main_category_slug", "slug", "image")
        read_only_fields = ('id',)

    def create(self, validated_data):
        # Retrieve or create the main category based on the slug
        main_category_slug = validated_data.pop('main_category', None)
        if main_category_slug:
            main_category, created = MealCategory.objects.get_or_create(slug=main_category_slug)
            validated_data['main_category'] = main_category

        validated_data["created_from"] = self.context["request"].user.restaurant
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle main category update
        main_category_slug = validated_data.pop('main_category', None)
        if main_category_slug:
            main_category, created = MealCategory.objects.get_or_create(slug=main_category_slug)
            instance.main_category = main_category

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SubCategoryHotelAdminSerializer(serializers.ModelSerializer):
    main_category = MealCategorySerializer(read_only=True)  # If main_category is a foreign key
    main_category_slug = serializers.SlugField(write_only=True, required=False, allow_unicode=True,
                                               source='main_category')  # For write operations

    class Meta:
        model = SubCategory
        fields = ("id", "name_az", "name_tr", "name_ar", "name_en", "name_ru", "name_ko", "order", "main_category",
                  "main_category_slug", "slug", "image")
        read_only_fields = ('id',)

    def validate(self, data):
        if (data.get('name_az') is None or data.get('name_az') == '') and data.get('name_en'):
            data['name_az'] = data['name_en']
        return data

    def create(self, validated_data):
        # Retrieve or create the main category based on the slug
        main_category_slug = validated_data.pop('main_category', None)
        if main_category_slug:
            main_category, created = MealCategory.objects.get_or_create(slug=main_category_slug)
            validated_data['main_category'] = main_category

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle main category update
        main_category_slug = validated_data.pop('main_category', None)
        if main_category_slug:
            main_category, created = MealCategory.objects.get_or_create(slug=main_category_slug)
            instance.main_category = main_category

        if "image" in validated_data:
            image = validated_data.pop("image")
            if image is None or image == "":
                instance.image.delete(save=False)
                instance.image = None
            else:
                instance.image = image

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MealUpdateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = (
            'name',
            'category',
            'price',
            'vegan',
            'ingredient',
            'is_active',
            'is_halal',
            'is_new',
            'calorie',
            'etp',
            'slug',
            'iiko_id'
        )


class GetMealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    category = SimpleGetSubcategorySerializer(read_only=True)

    class Meta:
        model = Meal
        fields = (
            "name", "category", "price", "image", "vegan", "ingredient", "is_active", "is_halal", "is_new", "calorie",
            "etp", "slug", "iiko_id")
        read_only_fields = ("slug",)

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):

            return f"{obj.image.url}"
        else:
            return None


class GetMealAdminSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    category = SimpleGetSubcategorySerializer(read_only=True)

    class Meta:
        model = Meal
        fields = (
            "name_az", "name_tr", "name_ar", "name_en", "name_ru", "name_ko", "category", "price", "image", "vegan",
            "ingredient_az", "ingredient_tr", "ingredient_ar", "ingredient_en", "ingredient_ru", "ingredient_ko",
            "is_active", "is_halal", "is_new", 'calorie', "etp", "slug", "priority", "iiko_id")
        read_only_fields = ("slug",)

    def get_image(self, obj):
        if MealImage.objects.filter(meal=obj).exists():
            image = obj.images.first()
            return image.image.url
        elif obj.image and hasattr(obj.image, 'url'):
            return f"{obj.image.url}"
        else:
            return None

    def get_price(self, obj):
        if not obj.price:
            try:
                price = obj.sizes.first().price
            except:
                price = None
        else:
            price = obj.price
        return price


class GetCategorySerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    icon = serializers.CharField()  # Add fields as needed
    slug = serializers.CharField()

    class Meta:
        model = MealCategory
        fields = ("name", "icon", "order", "slug")

    def get_name(self, obj):
        return obj.name


# class GetSubCategorySerializer(serializers.Serializer):
#     name = serializers.SerializerMethodField()
#     main_category = GetCategorySerializer()
#     slug = serializers.CharField()
#     class Meta:
#         model=SubCategory
#         fields=("name","main_category","slug")
#
#     def get_name(self,obj):
#         return obj.name

class UrlSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = (
            'id',
            'url'
        )


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = (
            'id',
            'name'
        )


class RestaurantPackageSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True)
    urls = UrlSerialzier(many=True)

    class Meta:
        model = RestaurantPackage
        fields = (
            'name',
            'features',
            'urls'
        )


class RestaurantLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetaurantLanguage
        fields = (
            'name',
        )


class RestaurantCampaignInQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCampaign
        fields = (
            'id',
            'cover'
        )


class RestaurantWorkingHoursSeriazlizer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantWorkingHour
        fields = (
            'weekday',
            'start',
            'end'
        )


class ScanQRSerializer(serializers.ModelSerializer):
    meals = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username')
    phone_number = serializers.CharField(source='user.phone_number')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    profile_photo = serializers.ImageField(source='user.profile_photo')
    package = RestaurantPackageSerializer()
    language = RestaurantLanguageSerializer(many=True)
    currency = CurrencySerializer(many=True)
    campaigns = RestaurantCampaignInQRSerializer(many=True)
    gender = serializers.CharField(source='user.gender')
    working_hours = serializers.SerializerMethodField(read_only=True)
    loyalty_discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = (
            'id', 'package', 'username', 'phone_number', 'working_hours', 'cover',
            'latitude', 'longitude', 'first_name', 'last_name', 'service_fee',
            'fbpixel', 'facebook', 'instagram', 'whatsapp', 'google', 'tripadvisor',
            'tiktok', 'address', 'currency', 'language', 'profile_photo', 'gender',
            'campaigns', 'meals', 'categories', 'loyalty_discount_percent',
        )
        read_only_fields = ('id',)

    def get_working_hours(self, obj):
        # Convert to dictionary in a single pass
        return {
            wh.weekday: {"start": wh.start, "end": wh.end}
            for wh in obj.workinghours.all()
        }

    def get_loyalty_discount_percent(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and getattr(user, 'is_loyal', False):
            return obj.loyalty_discount_percent
        return None

    def get_meals(self, obj):
        # Cache request user data
        request = self.context.get('request')
        user = request.user if request else None
        is_authenticated = user.is_authenticated if user else False
        client = getattr(user, 'client', None) if is_authenticated else None
        is_loyal = getattr(user, 'is_loyal', False) if is_authenticated else False

        # Use select_related to reduce the number of database queries
        meals = Meal.objects.filter(
            created_from=obj,
            category__isnull=False,
            category__main_category__isnull=False
        ).select_related(
            'category',
            'category__main_category',
            'created_from'
        ).prefetch_related(
            'sizes',
            'images'
        ).order_by("priority")

        if not meals.exists():
            return []

        # Get favorite meals in a single query
        favorite_meal_ids = set()
        if client:
            favorite_meal_ids = set(
                FavoriteMeal.objects.filter(
                    client=client,
                    meal__in=meals
                ).values_list('meal_id', flat=True)
            )

        # Prepare cache for category data to avoid repetitive attribute access
        main_categories_dict = {}
        subcategories_dict = {}
        categorized_meals = {}

        # Process meals in a single pass
        for meal in meals:
            main_category = meal.category.main_category
            subcategory = meal.category

            # Initialize category structures if needed
            if main_category.id not in main_categories_dict:
                main_categories_dict[main_category.id] = {
                    'category_id': main_category.id,
                    'category_name': main_category.name,
                    'category_icon': main_category.icon.url if main_category.icon else None,
                    'order': main_category.order,
                    'is_active': main_category.is_active,
                    'slug': main_category.slug,
                    'subcategories': []
                }
                categorized_meals[main_category.id] = {}

            if subcategory.id not in subcategories_dict:
                subcategories_dict[subcategory.id] = {
                    'id': subcategory.id,
                    'slug': subcategory.slug,
                    'name': subcategory.name,
                    'order': subcategory.order,
                    'image': subcategory.image.url if subcategory.image else None,
                    'meals': []
                }
                categorized_meals[main_category.id][subcategory.id] = subcategories_dict[subcategory.id]

            # Get meal price
            sizes = list(meal.sizes.all())
            price = meal.price if meal.price else (sizes[0].price if sizes else None)

            # Get meal image efficiently
            meal_images = list(meal.images.all())
            image_url = meal_images[0].image.url if meal_images else (meal.image.url if meal.image else None)

            # Process sizes data
            discount_percent = meal.created_from.loyalty_discount_percent if meal.created_from.loyalty_discount_percent > 0 else 0

            sizes_data = [
                {
                    'id': size.id,
                    'size': size.size,
                    'price': size.get_discounted_price() if is_loyal else size.price,
                    'discount_percent': discount_percent
                }
                for size in sizes
            ]

            # Create meal data
            meal_data = {
                'id': meal.id,
                'name': meal.name,
                'image': image_url,
                'price': price,
                'sizes': sizes_data,
                'vegan': meal.vegan,
                'ingredient': meal.ingredient,
                'is_active': meal.is_active,
                'is_halal': meal.is_halal,
                'is_new': meal.is_new,
                'slug': meal.slug,
                'etp': meal.etp,
                'is_favorite': meal.id in favorite_meal_ids,
                'iiko_id': meal.iiko_id,
                'discount_percent': discount_percent
            }

            # Add meal to appropriate subcategory
            categorized_meals[main_category.id][subcategory.id]['meals'].append(meal_data)

        # Build the final meal structure
        structured_meals = []
        for main_cat_id, main_cat_data in sorted(main_categories_dict.items(), key=lambda x: x[1]['order']):
            # Sort and add subcategories to main category
            main_cat_copy = main_cat_data.copy()
            subcats = []

            for subcat_id, subcat_data in sorted(categorized_meals[main_cat_id].items(), key=lambda x: x[1]['order']):
                subcats.append(subcat_data)

            main_cat_copy['subcategories'] = subcats
            structured_meals.append(main_cat_copy)

        return structured_meals

    def get_categories(self, obj):
        # Optimize category retrieval with a direct query
        subcategory_ids = Meal.objects.filter(
            created_from=obj,
            category__isnull=False
        ).values_list('category', flat=True).distinct()

        if not subcategory_ids:
            return []

        # Get main categories in one query with prefetch
        main_category_ids = SubCategory.objects.filter(
            id__in=subcategory_ids
        ).values_list('main_category', flat=True).distinct()

        if not main_category_ids:
            return []

        # Get categories with prefetched subcategories
        categories = MealCategory.objects.filter(
            id__in=main_category_ids
        ).prefetch_related(
            Prefetch('subcategories', queryset=SubCategory.objects.filter(id__in=subcategory_ids))
        ).order_by('order')

        # Use a cached serializer instance
        if not hasattr(self, '_category_serializer'):
            self._category_serializer = GetMealCategorySerializer(many=True)

        self._category_serializer.instance = categories
        return self._category_serializer.data


class RestaurantSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'facebook',
            'instagram',
            'whatsapp',
            'tiktok',
            'address_az',
            'address_tr',
            'address_ar',
            'address_en',
            'address_ru',
            'address_ko'
        )


class RestaurantSocialMediaAdminSerializer(serializers.ModelSerializer):
    working_hours = serializers.SerializerMethodField(read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            'facebook',
            'instagram',
            'whatsapp',
            'tiktok',
            'phone_number',
            'service_fee',
            'address_az',
            'address_tr',
            'address_ar',
            'address_en',
            'address_ru',
            'address_ko',
            'working_hours'
        )

    def get_working_hours(self, obj):
        data = obj.workinghours.all()
        result = {}
        for i in data:
            result[i.weekday] = {
                "start": i.start,
                "end": i.end
            }
        return result


class RestaurantSocialMediaUpdateSerializer(serializers.ModelSerializer):
    working_hours = serializers.JSONField(write_only=True)
    phone_number = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Restaurant
        fields = (
            'facebook',
            'instagram',
            'whatsapp',
            'tiktok',
            'service_fee',
            'phone_number',
            'address_az',
            'address_tr',
            'address_ar',
            'address_en',
            'address_ru',
            'address_ko',
            'working_hours'
        )

    def update(self, instance, validated_data):
        restaurant = self.context['request'].user.restaurant
        if "working_hours" in validated_data:
            working_hours = validated_data.pop('working_hours')

            for key, value in working_hours.items():
                if not RestaurantWorkingHour.objects.filter(restaurant=restaurant, weekday=key).exists():
                    working = RestaurantWorkingHour.objects.create(restaurant=restaurant, weekday=key,
                                                                   start=value['start'], end=value['end'])
                else:
                    working = RestaurantWorkingHour.objects.get(restaurant=restaurant, weekday=key)
                    working.start = value['start']
                    working.end = value['end']
                    working.save()

        if "phone_number" in validated_data:
            phone = validated_data.pop("phone_number")
            user = restaurant.user
            user.phone_number = phone
            user.save()

        return super().update(instance, validated_data)


class RestaurantSocialMediaReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'google',
            'tripadvisor'
        )


class GeoLocationSerializer(serializers.Serializer):
    username = serializers.CharField(source='user.username')
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = Restaurant
        fields = ("username", "latitude", "longitude")


class BasketItemCreateSeriazlier(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = (
            'meal',
            'size',
            'quantity'
        )

    def validate(self, attrs):
        client = self.context['request'].user.client
        if Basket.objects.filter(client=client, is_completed=False).exists():
            basket = Basket.objects.get(client=client, is_completed=False)
        else:
            basket = Basket.objects.create(client=client)
        if BasketItem.objects.filter(basket=basket, meal=attrs['meal'], size=attrs['size']).exists():
            raise ValidationError("This meal is already in the basket")
        price = attrs['meal'].number_price if 'meal' in attrs else attrs['size'].meal.number_price
        attrs['basket'] = basket
        attrs['client'] = client
        attrs['price'] = price
        return super().validate(attrs)


class BasketItemSerializer(serializers.ModelSerializer):
    meal = MealSerializer()

    class Meta:
        model = BasketItem
        fields = (
            'id',
            'meal',
            'size',
            'quantity',
            'price'
        )


class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True)
    client = serializers.CharField(source='client.user.username')

    class Meta:
        model = Basket
        fields = (
            'id',
            'client',
            'is_completed',
            'created_at',
            'items'
        )


class BasketItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = (
            'quantity',
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'basket',
        )

    def validate(self, attrs):
        client = self.context['request'].user.client
        if Basket.objects.filter(client=client, is_completed=False).exists():
            basket = Basket.objects.get(client=client, is_completed=False)
        else:
            raise ValidationError("Basket is empty")
        attrs['basket'] = basket
        attrs['client'] = client
        return super().validate(attrs)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id',
            'client',
            'basket',
            'total_price',
            'is_completed',
            'created_at'
        )


class FavoriteMealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteMeal
        fields = (
            'meal',
        )

    def validate(self, attrs):
        client = self.context['request'].user.client
        if FavoriteMeal.objects.filter(client=client, meal=attrs['meal']).exists():
            raise ValidationError("This meal is already in the favorites")
        attrs['client'] = client
        return super().validate(attrs)


class RestaurantMobileDetailsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    phone_number = serializers.CharField(source='user.phone_number')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    profile_photo = serializers.ImageField(source='user.profile_photo')
    package = RestaurantPackageSerializer()
    language = RestaurantLanguageSerializer(many=True)
    currency = CurrencySerializer(many=True)
    campaigns = RestaurantCampaignInQRSerializer(many=True)
    gender = serializers.CharField(source='user.gender')
    working_hours = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = (
            'id',
            'package',
            'username',
            'phone_number',
            'working_hours',
            'cover',
            'latitude',
            'longitude',
            'first_name',
            'last_name',
            'service_fee',
            'fbpixel',
            'facebook',
            'instagram',
            'whatsapp',
            'google',
            'tripadvisor',
            'tiktok',
            'address',
            'currency',
            'language',
            'profile_photo',
            'gender',
            'campaigns',
        )
        read_only_fields = ('id',)

    def get_working_hours(self, obj):
        data = obj.workinghours.all()
        result = {}
        for i in data:
            result[i.weekday] = {
                "start": i.start,
                "end": i.end
            }
        return result


class RestaurantMobileMealsSerializer(serializers.ModelSerializer):
    meals = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = (
            'meals',
            'categories',
        )

    def get_meals(self, obj):
        meals = Meal.objects.filter(created_from=obj).order_by("priority").select_related('category',
                                                                                          'category__main_category')

        if not meals:
            return []

        categorized_meals = defaultdict(lambda: defaultdict(list))
        for meal in meals:
            if meal.category and meal.category.main_category:
                main_category = meal.category.main_category
                subcategory = meal.category
                sizes = meal.sizes.all()

                if not meal.price:
                    try:
                        price = sizes.first().price if sizes.exists() else None
                    except:
                        price = None
                else:
                    price = meal.price
                user = self.context['request'].user
                is_loyal = user.is_authenticated and getattr(user, 'is_loyal', False)
                client = getattr(user, 'client', None) if user.is_authenticated else None

                is_favorite = FavoriteMeal.objects.filter(client=client, meal=meal).exists() if client else False

                sizes_data = [
                    {
                        'id': size.id,
                        'size': size.size,
                        'price': size.get_discounted_price() if is_loyal else size.price,
                        'discount_percent': meal.created_from.loyalty_discount_percent if meal.created_from.loyalty_discount_percent > 0 else 0
                    } for size in sizes
                ]

                meal_data = {
                    'id': meal.id,
                    'name': meal.name,
                    'image': f"{meal.images.first().image.url}"
                          if MealImage.objects.filter(meal=meal).exists()
                          else f"{meal.image.url}",
                    'price': price,
                    'sizes': sizes_data,
                    'vegan': meal.vegan,
                    'ingredient': meal.ingredient,
                    'is_active': meal.is_active,
                    'is_halal': meal.is_halal,
                    'is_new': meal.is_new,
                    'slug': meal.slug,
                    'etp': meal.etp,
                    'is_favorite': is_favorite,
                    'iiko_id': meal.iiko_id,
                    'discount_percent': meal.created_from.loyalty_discount_percent if meal.created_from.loyalty_discount_percent > 0 else 0
                }
                categorized_meals[main_category][subcategory].append(meal_data)
        
        structured_meals = []
        for main_category in categorized_meals:
            subcategories_list = []
            for subcategory in categorized_meals[main_category]:
                subcategories_list.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'meals': categorized_meals[main_category][subcategory],
                    'order': subcategory.order,
                    'image': subcategory.image.url if subcategory.image else None,
                })
            structured_meals.append({
                'category_id': main_category.id,
                'category_name': main_category.name,
                'subcategories': subcategories_list,
                'category_icon': main_category.icon.url,
                'order': main_category.order,
                'is_active': main_category.is_active,
                'slug': main_category.slug,
            })
        return structured_meals

    def get_categories(self, obj):
        meals = Meal.objects.filter(created_from=obj)
        if meals:
            subcategory_ids = meals.values_list('category', flat=True).distinct()
            subcategories = SubCategory.objects.filter(id__in=subcategory_ids)
            category_ids = subcategories.values_list('main_category', flat=True).distinct()
            meal_categories = MealCategory.objects.filter(id__in=category_ids).order_by('order')
            serializer = GetMealCategorySerializer(meal_categories, many=True)
            return serializer.data
        return []


class MealPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['priority']
