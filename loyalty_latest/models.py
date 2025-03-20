from django.db import models
from base_user.models import Restaurant , Hotel , User
from datetime import datetime
# Create your models here.
TYPE_CHOICES = [
    ('QR','qr_code'),
    ('Barcode','barcode')
]

LEVEL_CHOICES = [
    ('none','None'),
    ('Bronze','bronze'),
    ('Silver','silver'),
    ('Gold','gold'),
]
DEVICE_TYPE = [
    ('',''),
    ('IOS','ios'),
    ('Android','android')
]

LANGUAGE_CHOICES = [
    ('EN', 'English'),
    ('RU', 'Russian'),
    ('AZ', 'Azerbaijan')
]

CARD_TYPES = [
    ('bonus','Bonus'),
    ('loyalty','Loyalty'),
    ('threshold','Discount'),

]

class Layout(models.Model):
    layout_name = models.CharField(max_length=255,default='')
    layout_banner = models.ImageField(upload_to='loyalty_layout_banners/')
    layout_logo = models.ImageField(upload_to='loyalty_logo_icons/')
    layout_type = models.CharField(choices=TYPE_CHOICES,max_length=255,default='QR')
    layout_background_color = models.CharField(max_length=255)
    text_color = models.CharField(max_length=255)
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    does_threshold = models.BooleanField(default=False)
    threshold_ranges = models.JSONField(default=list) 

class UserCard(models.Model):
    card_user_id = models.CharField(max_length=255)
    device = models.CharField(max_length=255,default='')
    layout = models.ForeignKey(Layout,on_delete=models.CASCADE)
    card_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    email = models.EmailField(default='',null=True,blank=True)
    bonuses = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    loyalty_level = models.CharField(choices=LEVEL_CHOICES,default='',max_length=255)
    deviceToken = models.CharField(max_length=255,default='')
    loyalty_balance = models.FloatField(default=0)
    is_confirmed = models.BooleanField(default=False)
    download_hash = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant , on_delete=models.CASCADE, null = True , blank = True)
    hotel = models.ForeignKey(Hotel , on_delete=models.CASCADE , null = True , blank = True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    card_user_birth_date = models.DateField(default=datetime(2000, 1, 1, 12, 0))
    birth_date_discount = models.IntegerField(default=0)
    cashback = models.IntegerField(default=0)
    birthdate_prize = models.CharField(default='',max_length=255)
    customer_lang = models.CharField(choices=LANGUAGE_CHOICES,max_length=255,default='AZ')
    passed_threshold = models.JSONField(default=list)



class Passes(models.Model):
    device_type = models.CharField(choices=DEVICE_TYPE,max_length=255,default='')
    pass_file = models.FileField(upload_to='pass_files/',null=True,blank=True)
    google_add_card = models.CharField(max_length=50000,default='')
    user_card = models.ForeignKey(UserCard,on_delete=models.CASCADE)