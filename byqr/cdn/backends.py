from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.azure_storage import AzureStorage

class StaticRootS3Boto3Storage(AzureStorage):
    location = 'static'


class MediaRootS3Boto3Storage(AzureStorage):
    location = 'media'
