from django.db import models
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from base_user.models import Museum
from gtts import gTTS
from googletrans import Translator
import os


class Exhibit(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    museum = models.ForeignKey(Museum, on_delete=models.SET_NULL,
                               null=True,
                               blank=True)
    qr_code = models.ImageField(upload_to="exhibit", null=True, blank=True)
    sound = models.FileField(upload_to="exhibit", null=True, blank=True)
    video = models.FileField(upload_to="exhibit", null=True, blank=True)
    text = models.TextField()
    additional_text = models.TextField(
                                       null=True,
                                       blank=True
                                       )
    image_1 = models.ImageField(upload_to="exhibit/", null=True, blank=True)
    image_2 = models.ImageField(upload_to="exhibit/", null=True, blank=True)
    image_3 = models.ImageField(upload_to="exhibit/", null=True, blank=True)
    image_4 = models.ImageField(upload_to="exhibit/", null=True, blank=True)
    image_5 = models.ImageField(upload_to="exhibit/", null=True, blank=True)

    def __str__(self):
        return self.museum.name

    class Meta:
        verbose_name = "Exhibit"
        verbose_name_plural = "Exhibits"






