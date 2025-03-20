AWS_ACCESS_KEY_ID='AKIAXYKJXDFWM6X22HEE'
AWS_SECRET_ACCESS_KEY='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'
# AWS_ACCESS_KEY_ID='AKIAXYKJXDFWFIML3GVK'
# AWS_SECRET_ACCESS_KEY='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'
AWS_STORAGE_BUCKET_NAME="byqr-backend"
# AWS_S3_ENDPOINT_URL="https://fra1.digitaloceanspaces.com"
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}



# AWS_LOCATION = 'https://byqr-cdn.fra1.digitaloceanspaces.com'
DEFAULT_FILE_STORAGE = 'byqr.cdn.backends.MediaRootS3Boto3Storage'
STATICFILES_STORAGE = 'byqr.cdn.backends.StaticRootS3Boto3Storage'
