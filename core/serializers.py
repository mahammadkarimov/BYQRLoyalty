from rest_framework import serializers
from .models import RestaurantDiscounts, Payment, Currency, UserFAQ


#  created_from=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
#       name=models.CharField(max_length=100)
#       image=models.ImageField(upload_to="discounts")
#       is_active=models.BooleanField(default=True)
#       expiration_date=models.DateTimeField(null=True, blank=True)
#       created_date = models.DateField(auto_now_add=True, null=True, blank=True)

class RestaurantPostDiscountSerializer(serializers.ModelSerializer):
    # expiration_date = serializers.DateTimeField(format='%d %m %Y')
    class Meta:
        model = RestaurantDiscounts
        fields = ("name", "image", "is_active", "expiration_date", "slug")

    def create(self, validated_data):
        validated_data["created_from"] = self.context["request"].user
        return super().create(validated_data)


class RestaurantGetDiscountSerializer(serializers.ModelSerializer):
    expiration_date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantDiscounts
        fields = ("name", "image", "is_active", "expiration_date", "slug")

    def get_expiration_date(self, obj):
        if obj.expiration_date:

            return obj.expiration_date.strftime("%d-%m-%Y")  # 12.04.2023
        else:
            return obj.expiration_date

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):

            return f"{obj.image.url}"
        else:
            return None

    # def create(self, validated_data):

    #     validated_data["created_from"]=self.context["request"].user
    #     return super().create(validated_data)


class PaymentCreateSerialzier(serializers.Serializer):
    table_id = serializers.CharField()
    rate = serializers.IntegerField(required=False)
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    currency = serializers.IntegerField()
    description = serializers.CharField(required=False)
    language = serializers.CharField()


class CurrencySerialzier(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = (
            'id',
            'name'
        )


class PaymentSuccessResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    redirect_url = serializers.URLField()
    transaction = serializers.CharField()


class CallBackSeriazlier(serializers.Serializer):
    data = serializers.CharField()
    signature = serializers.CharField()


class PaymentStatusSerializer(serializers.Serializer):
    transaction = serializers.CharField()


class PaymentStatusResponseSerialzier(serializers.Serializer):
    status = serializers.CharField()
    code = serializers.IntegerField()
    message = serializers.CharField()
    transaction = serializers.CharField()
    order_id = serializers.CharField()
    bank_tansaction = serializers.CharField()
    bank_response = serializers.CharField()
    card_name = serializers.CharField()
    card_mask = serializers.CharField()
    rrn = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    other_attr = serializers.CharField()


class CardRegisterSerialzier(serializers.Serializer):
    language = serializers.CharField()
    description = serializers.CharField(required=False)
    success_redirect_url = serializers.CharField(required=False)
    error_redirect_url = serializers.CharField(required=False)


class CardRegisterResponseSerialzier(serializers.Serializer):
    status = serializers.CharField()
    redirect_url = serializers.URLField()
    card_id = serializers.CharField()


class PayWithSavedCardSerialzier(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    currency = serializers.IntegerField()
    card_id = serializers.CharField()
    language = serializers.CharField()
    waiter_id = serializers.CharField()
    rate = serializers.IntegerField()
    description = serializers.CharField(required=False)


class PaymentWithSavedCardResponseSerialzier(serializers.Serializer):
    status = serializers.CharField()
    transaction = serializers.CharField()
    bank_tansaction = serializers.CharField()
    bank_response = serializers.CharField()
    rrn = serializers.IntegerField()
    card_name = serializers.CharField()
    card_mask = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    message = serializers.CharField()


class PayAndSaveCardSerialzier(serializers.Serializer):
    waiter_id = serializers.CharField()
    rate = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    currency = serializers.IntegerField()
    description = serializers.CharField()
    language = serializers.CharField()
    success_redirect_url = serializers.CharField(required=False)
    error_redirect_url = serializers.CharField(required=False)


class PayAndSaveCardResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    redirect_url = serializers.URLField()
    card_id = serializers.CharField()
    transaction = serializers.CharField()


class CreateRefundSerialzier(serializers.Serializer):
    waiter_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    currency = serializers.IntegerField()
    card_id = serializers.CharField()
    language = serializers.CharField()
    description = serializers.CharField(required=False)


class PaymentListSerialzier(serializers.ModelSerializer):
    currency = serializers.CharField(source='currency.name')

    class Meta:
        model = Payment
        fields = (
            'amount',
            'currency',
            'created_at'
        )


class ApplePaySerialzier(serializers.Serializer):
    id = serializers.IntegerField()
    token = serializers.CharField()
    billing_contact = serializers.CharField()


class UserFAQSerialzier(serializers.ModelSerializer):
    class Meta:
        model = UserFAQ
        fields = (
            'id',
            'question',
            'answer'
        )


class CorporativeWebsiteContactSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    category = serializers.CharField()

class EPointTokenSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)
    description = serializers.CharField()
    waiter = serializers.CharField()
    currency = serializers.IntegerField()
    table_id = serializers.CharField()
    rate = serializers.IntegerField(required=False)