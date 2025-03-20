from django.db import models
# teklifin sekili, adi ve ne vaxta qeder kecerli oldugu gosterilir. 
from django.contrib.auth import get_user_model
from slugify import slugify
from base_user.models import Restaurant
from base_user.models import Waiter


class RestaurantDiscounts(models.Model):
  created_from=models.ForeignKey(Restaurant,on_delete=models.CASCADE,null=True,blank=True)
  name=models.CharField(max_length=100,unique=True)
  image=models.ImageField(upload_to="discounts")
  is_active=models.BooleanField(default=True)
  expiration_date=models.DateTimeField(null=True, blank=True)
  created_date = models.DateField(auto_now_add=True, null=True, blank=True)
  slug=models.SlugField(null=True,blank=True)


  def save(self, *args, **kwargs):
    self.slug = slugify(self.name)
    return super(RestaurantDiscounts, self).save(*args, **kwargs)
     

class Currency(models.Model):
  name = models.CharField(max_length=50)

  class Meta:
    verbose_name = 'Currency'
    verbose_name_plural = 'Currencies'
  
  def __str__(self) -> str:
    return self.name


class Payment(models.Model):
  amount = models.DecimalField(max_digits=5, decimal_places=2)
  net = models.DecimalField(max_digits=5, decimal_places=2, default=0)
  currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='payments')
  order_id = models.CharField(max_length=100)
  refund_id = models.CharField(max_length=100, null=True, blank=True)
  description = models.TextField(null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  transaction_id = models.CharField(max_length=30, null=True, blank=True)
  refund_transaction_id = models.CharField(max_length=30, null=True, blank=True)
  waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE, related_name='tips')
  card_name = models.CharField(max_length=200, null=True, blank=True)
  card_mask = models.CharField(max_length=200, null=True, blank=True)
  waiter_card_name = models.CharField(max_length=200, null=True, blank=True)
  waiter_card_mask = models.CharField(max_length=100, null=True, blank=True)
  is_successful = models.BooleanField(default=False)
  is_completed = models.BooleanField(default=False)

  def __str__(self) -> str:
    return f'{self.amount} {self.currency.name}'


class UserFAQ(models.Model):
  question = models.CharField(max_length=255)
  answer = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return self.question
