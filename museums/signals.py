from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from io import BytesIO
from .models import Exhibit
from googletrans import Translator
from gtts import gTTS
from django.core.files.base import ContentFile
import io


@receiver(post_save, sender=Exhibit)
def generate_qr_code(sender, instance, created, **kwargs):
    """
    This function generates the QR code for the Exhibit after it's saved.
    It runs only when a new Exhibit is created.
    """
    if created:
        qr_url = f"https://museum.byqr.az/az/museum/{instance.museum.user.username}/{instance.id}/"

        qr = qrcode.make(qr_url)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')
        qr_image = ContentFile(qr_io.getvalue(), f"qr_code_{instance.id}.png")

        instance.qr_code.save(f"qr_code_{instance.name}.png", qr_image, save=False)

        instance.save()


@receiver(post_save, sender=Exhibit)
def generate_translations_and_audio(sender, instance, created, **kwargs):
    """
    Signal handler to generate translations and audio files for Exhibit.
    """
    if created:
        translator = Translator()
        translations = {
            "en": "text_en",
            "ru": "text_ru",
            "ko": "text_ko",
            "ar": "text_ar",
        }
        for lang, text_field in translations.items():
            audio_field = f"sound_{lang}"
            if not getattr(instance, text_field):
                try:
                    translated_text = translator.translate(instance.text_az, src="az", dest=lang).text
                    setattr(instance, text_field, translated_text)

                    tts = gTTS(text=translated_text, lang=lang)
                    audio_file = io.BytesIO()
                    tts.write_to_fp(audio_file)
                    audio_file.seek(0)

                    file_name = f"exhibit/{lang}_{instance.id}.mp3"
                    getattr(instance, audio_field).save(file_name, ContentFile(audio_file.read()), save=False)
                except Exception as e:
                    print(f"Error generating translation or audio for {lang}: {e}")

        instance.save()
