import requests
from django.core.files.base import ContentFile
from io import BytesIO
from django.core.files.storage import default_storage


def download_image_from_url(url: str, field_name: str):
    try:
        # Make an HTTP GET request to fetch the image
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request fails

        # Open the image as bytes
        image_content = BytesIO(response.content)
        file_name = url.split("/")[-1]  # Extract the file name from the URL

        # Create a content file from the image bytes
        content_file = ContentFile(image_content.read(), name=file_name)

        # Store the file in the Django media storage
        file_path = default_storage.save(f'layouts_{field_name}/{file_name}', content_file)

        return file_path
    except requests.exceptions.RequestException as e:
        raise Exception(("Image download failed: %s") % str(e))
