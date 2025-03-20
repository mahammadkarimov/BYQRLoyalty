from django.db import models
from services.choices import PROGRAMS

class Programs(models.Model):
    iiko_id = models.CharField(max_length=100)
    name = models.CharField(max_length=20,
                            choices=PROGRAMS)

    def __str__(self):
        return self.name + " -> " + self.iiko_id

    class Meta:
        ordering = ("name",)
        verbose_name = "Program"
        verbose_name_plural = "Programs"


class LoyaltyCategories(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    iiko_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    restaurants = models.ManyToManyField('base_user.Restaurant',
                                         null=True,
                                         blank=True)

    def __str__(self):
        return self.name + " -> " + self.iiko_id + " -> " + self.program.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Loyalty Category"
        verbose_name_plural = "Loyalty Categories"



class Coupons(models.Model):
    restaurant = models.ForeignKey("base_user.Restaurant", on_delete=models.SET_NULL,
                                   null=True, blank=True)
    client = models.ForeignKey("base_user.Client", on_delete=models.SET_NULL,
                               null=True, blank=True)
    image = models.ImageField(upload_to="client_coupons/")
    number = models.CharField(max_length=255,verbose_name='Number of Coupon')
    def __str__(self):
        return f"{self.client.user.username}-{self.restaurant.user.username}-{self.number}"

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"


