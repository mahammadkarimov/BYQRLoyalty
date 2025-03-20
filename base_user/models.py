import random
import string
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
import uuid
from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, BaseUserManager
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from loyalty.models import LoyaltyCategories

USER_MODEL = settings.AUTH_USER_MODEL


class MyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_type = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True, error_messages={
        'unique': "A user with that email already exists.",
    })
    profile_photo = models.FileField(upload_to='profile_pic', default="default.png", null=True, blank=True)
    gender = models.CharField(choices=(
        ("Male", "Male"),
        ("Female", "Female"),
    ), default="Male", max_length=30)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
    )

    is_verified = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_loyal = models.BooleanField(
        default=False
    )
    date_joined = models.DateField(default=timezone.now, null=True, blank=True)

    fcm_token = models.TextField(null=True,
                                 blank=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = ('email')
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def __str__(self):
        return self.first_name


User = MyUser()


class Feature(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


class RestaurantPackage(models.Model):
    name = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='package_cover', null=True, blank=True)
    features = models.ManyToManyField(Feature, null=True, blank=True, related_name='packages')

    def __str__(self) -> str:
        return self.name


class Url(models.Model):
    url = models.CharField(max_length=200)
    package = models.ForeignKey(RestaurantPackage, on_delete=models.CASCADE, related_name='urls')

    def __str__(self) -> str:
        return self.url


class RetaurantLanguage(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)

    def __str__(self) -> str:
        return f'{self.name} - {self.symbol}'


class Currency(models.Model):
    currency = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='currencies')
    language = models.ForeignKey(RetaurantLanguage, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='currencies')

    def __str__(self) -> str:
        return f"{self.currency.name} - {self.language}"


class RestaurantCategory(models.Model):
    name = models.CharField(max_length=100, )
    image = models.ImageField(upload_to="restaurant-category",
                              null=True,
                              blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Restaurant Category"
        verbose_name_plural = "Restaurant Categories"


class RestaurantSubCategory(models.Model):
    parent = models.ForeignKey(RestaurantCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Restaurant Sub Category"
        verbose_name_plural = "Restaurant Sub Categories"


class Restaurant(models.Model):
    terminal_group_id = models.CharField(max_length=100, null=True, blank=True)
    organization_id = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    cover = models.ImageField(upload_to='restaurant_cover', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    distance_area = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, null=True, blank=True, related_name='restaurants')
    show_tip_card = models.BooleanField(default=True)
    package = models.ForeignKey(RestaurantPackage, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='restaurants')
    category = models.ForeignKey(RestaurantSubCategory, on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True)
    slug = models.SlugField(null=True, blank=True, allow_unicode=True)
    language = models.ManyToManyField(RetaurantLanguage, blank=True, null=True, related_name='restaurants')
    currency = models.ManyToManyField(Currency, null=True, blank=True, related_name='restaurants')
    service_fee = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    whatsapp = models.URLField(null=True, blank=True)
    google = models.URLField(null=True, blank=True)
    tripadvisor = models.URLField(null=True, blank=True)
    tiktok = models.URLField(null=True, blank=True)
    fbpixel = models.CharField(max_length=100, null=True, blank=True)

    loyalty_discount_percent = models.IntegerField(default=0)
    is_popular = models.BooleanField(default=False)
    has_technical_service = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username, allow_unicode=True) + uuid.uuid4().hex[:6].upper()
        return super(Restaurant, self).save(*args, **kwargs)

    def average_rating(self):
        result = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return result if result else 0

    def review_count(self):
        return self.reviews.count()

    def __str__(self):
        return self.user.username

    def restaurant_name(self):
        return f'{self.user.first_name} {self.user.last_name}'


class RestaurantWorkingHour(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='workinghours')
    weekday = models.CharField(max_length=50, null=True, blank=True)
    start = models.CharField(max_length=50, null=True, blank=True)
    end = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.restaurant.user.username}"


class RestaurantCampaign(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=200)
    cover = models.ImageField(upload_to='campaign_cover', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class RestaurantReview(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey("Client", on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    review = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.rating}'


class RestaurantStory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='stories')
    cover = models.ImageField(upload_to='story_cover', null=True, blank=True)
    is_activate = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.restaurant.user.username

    class Meta:
        ordering = ['-created_at']


class Waiter(models.Model):
    waiter_id = models.CharField(max_length=10, null=True, blank=True, unique=True)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='waiter')
    slug = models.SlugField(null=True, blank=True, allow_unicode=True)
    notification_token = models.TextField(null=True, blank=True)
    card_id = models.CharField(max_length=100, null=True, blank=True)
    card_id_update = models.CharField(max_length=100, null=True, blank=True)
    is_card_saved = models.BooleanField(default=False)
    card_name = models.CharField(max_length=200, null=True, blank=True)
    card_mask = models.CharField(max_length=100, null=True, blank=True)
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True, related_name='waiters')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.first_name + self.user.last_name, allow_unicode=True) + uuid.uuid4().hex[
                                                                                              :6].upper()
        return super(Waiter, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Interest(models.Model):
    title = models.CharField(max_length=250)
    icon = models.ImageField(upload_to='interesetIcons')

    def __str__(self) -> str:
        return self.title


class Client(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='client')
    interests = models.ManyToManyField(Interest, blank=True, null=True, related_name='client')
    birthday = models.DateField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)

    barcode_image = models.ImageField(upload_to="barcodes", null=True, blank=True)
    card_id = models.CharField(max_length=16, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.first_name + self.user.last_name) + uuid.uuid4().hex[:6].upper()
        return super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class ClientRelationsWRestaurants(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Client and Restaurant"
        verbose_name_plural = "Clients and Restaurants"


class Hotel(models.Model):
    address = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    distance_area = models.FloatField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hotel')
    slug = models.SlugField(null=True, blank=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username, allow_unicode=True) + uuid.uuid4().hex[:6].upper()
        return super(Hotel, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class FavoriteRestaurant(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='favorites')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='favorite_restaurants')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.client.user.email}-{self.restaurant.user.username}'


class EventGenres(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Event Genre"
        verbose_name_plural = "Event Genres"


class EventTypes(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Event Type"
        verbose_name_plural = "Event Types"


class RestaurantEvent(models.Model):
    name = models.CharField(max_length=150)
    age = models.CharField(max_length=100)
    genre = models.ForeignKey(EventGenres, on_delete=models.SET_NULL,
                              null=True, blank=True)
    music_type = models.ForeignKey(EventTypes, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    entry_information = models.TextField()
    description = models.TextField()
    phone = models.CharField(max_length=100)
    address = models.TextField()
    map_url = models.TextField()

    start_date = models.CharField(max_length=100, )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Restaurant Event"
        verbose_name_plural = "Restaurant Events"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True) + uuid.uuid4().hex[:6].upper()
        return super(RestaurantEvent, self).save(*args, **kwargs)


class EventImages(models.Model):
    event = models.ForeignKey(RestaurantEvent, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="event_images", null=True, blank=True)

    def __str__(self):
        return self.event.name

    class Meta:
        verbose_name = "Event Image"
        verbose_name_plural = "Event Images"


class Museum(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="museum")
    name = models.CharField(max_length=200)
    background_image = models.ImageField(upload_to="museum")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Museum"
        verbose_name_plural = "Museums"


class LoyalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="loyal_users")
    first_name = models.CharField(max_length=200, )
    last_name = models.CharField(max_length=200, )
    father_name = models.CharField(max_length=200, )
    birthday_date = models.CharField(max_length=200, )
    phone = models.CharField(max_length=100, )
    address = models.CharField(max_length=100, )
    one_time_otp = models.CharField(max_length=100, null=True,
                                    blank=True)

    def generate_otp(self):
        """ 6 rəqəmli random OTP kodu yaradılır """
        self.one_time_otp = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return self.first_name + self.last_name + self.father_name

    class Meta:
        verbose_name = "Loyal user"
        verbose_name_plural = "Loyal users"


class LoyaltyCards(models.Model):
    client = models.ForeignKey(LoyalUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="loyal-card-images/")
    card_id = models.CharField(max_length=14, verbose_name="Card id", unique=True)

    def generate_card_id(self):
        """ 14 rəqəmli unikal kart ID yaradır """
        while True:
            random_id = ''.join(random.choices(string.digits, k=14))
            if not LoyaltyCards.objects.filter(card_id=random_id).exists():
                self.card_id = random_id
                break

    def generate_barcode(self):
        """ Barkod şəkli yaradıb image sahəsinə əlavə edir """
        ean = barcode.get('ean13', self.card_id[:12], writer=ImageWriter())  # EAN-13 barkod formatı
        buffer = BytesIO()
        ean.write(buffer)
        self.image.save(f"barcode_{self.card_id}.png", ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return self.client.first_name + self.restaurant.user.username

    class Meta:
        verbose_name = "Loyal card"
        verbose_name_plural = "Loyal cards"

    def save(self, *args, **kwargs):
        if not self.card_id:
            self.generate_card_id()
        self.generate_barcode()
        super().save(*args, **kwargs)
