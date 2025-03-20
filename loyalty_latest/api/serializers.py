from rest_framework import serializers
from rest_framework import serializers
from loyalty_latest.models import UserCard, Restaurant, Hotel, Layout
from loyalty_latest.utils.image import download_image_from_url

class UserCardSerializer(serializers.ModelSerializer):
    layout = serializers.PrimaryKeyRelatedField(queryset=Layout.objects.all())
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    class Meta:
        model = UserCard
        fields = [
            'id', 'user_id', 'device', 'layout', 'card_number', 'name', 'surname',
            'phone_number', 'email', 'bonuses', 'discount', 'loyalty_level',
            'deviceToken', 'loyalty_balance', 'is_confirmed', 'download_hash',
            'restaurant', 'hotel','cashback','card_user_birth_date','birth_date_discount','birthdate_prize','customer_lang'
        ]

    def validate_card_number(self, value):
        """
        Validate card_number, but only if it's being changed (i.e., it's part of the request).
        """
        if value and not self.instance:
            if UserCard.objects.filter(card_number=value).exists():
                raise serializers.ValidationError("Card number already exists.")
        return value

    def validate_phone_number(self, value):
        """
        Validate phone_number, but only if it's being changed.
        """
        if value and not self.instance:
            if not value.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")
        return value

    def validate_email(self, value):
        """
        Validate email, but only if it's being changed.
        """
        if value and not self.instance:
            if UserCard.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        return value

    def update(self, instance, validated_data):
        """
        Handle update logic for updating user card, making sure no overwrite issues.
        """
        # Don't validate card_number, email, or phone_number if they're not being updated
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    
class LayoutSerializer(serializers.ModelSerializer):
    layout_logo = serializers.ImageField(required=False)
    layout_banner = serializers.ImageField(required=False)
    class Meta:
        model = Layout
        fields = '__all__'

    def create(self, validated_data):
        layout_banner_url = validated_data.get('layout_banner_url')
        layout_logo_url = validated_data.get('layout_logo_url')

    
        if layout_banner_url:
            validated_data['layout_banner'] = download_image_from_url(layout_banner_url, '_layout_banners')
        
        if layout_logo_url:
            validated_data['layout_logo'] = download_image_from_url(layout_logo_url, '_logo_icons')

        return super().create(validated_data)

    def update(self, instance, validated_data):
        layout_banner_url = validated_data.get('layout_banner_url')
        layout_logo_url = validated_data.get('layout_logo_url')

        # Download the images from URLs if the URL is provided
        if layout_banner_url:
            instance.layout_banner = download_image_from_url(layout_banner_url, 'banners')
        
        if layout_logo_url:
            instance.layout_logo = download_image_from_url(layout_logo_url, 'logos')

        return super().update(instance, validated_data)