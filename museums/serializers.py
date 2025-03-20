from .models import Exhibit
from base_user.models import Museum
from rest_framework import serializers
from base_user.models import MyUser


class MuseumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Museum
        fields = ('id', 'user', 'name', 'background_image')


class ExhibitSerializer(serializers.ModelSerializer):
    museum = MuseumSerializer(read_only=True)

    class Meta:
        model = Exhibit
        fields = (
            'id',
            'name_az',
            'name_en',
            'name_ru',
            'name_ar',
            'name_ko',
            'museum',
            'qr_code',
            'sound_az',
            'sound_en',
            'sound_ru',
            'sound_ko',
            'sound_ar',
            'video_az',
            'video_en',
            'video_ru',
            'video_ko',
            'video_ar',
            'text_az',
            'text_en',
            'text_ru',
            'text_ko',
            'text_ar',
            'additional_text_az',
            'additional_text_en',
            'additional_text_ru',
            'additional_text_ko',
            'additional_text_ar',
            'image_1',
            'image_2',
            'image_3',
            'image_4',
            'image_5',

        )

    # def to_representation(self, instance):
    #     """Custom representation based on the language context."""
    #     lang = self.context.get('lang', None)
    #     data = super().to_representation(instance)
    #
    #     if lang:
    #         # Only keep fields relevant to the specified language
    #         language_fields = {'name_'+lang,'sound_' + lang, 'video_' + lang, 'text_' + lang}
    #         # Add any always-included fields
    #         language_fields.update({'id', 'museum', 'qr_code'})
    #         # Filter data to only include fields in `language_fields`
    #         data = {field: value for field, value in data.items() if field in language_fields}

    # return data
    def create(self, validated_data):
        user = self.context['request'].user
        # user = MyUser.objects.get(id=1)
        try:
            museum = Museum.objects.get(user=user)
        except Museum.DoesNotExist:
            raise serializers.ValidationError("User is not associated with a museum.")

        validated_data['museum'] = museum
        exhibit = Exhibit.objects.create(**validated_data)
        return exhibit
