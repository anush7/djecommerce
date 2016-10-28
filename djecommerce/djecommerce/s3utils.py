from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
from django.utils.deconstruct import deconstructible

StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
MediaRootS3BotoStorage  = lambda: S3BotoStorage(location='media')

# class StaticRootS3BotoStorage(S3BotoStorage):
#     location = 'static'

# class MediaRootS3BotoStorage(S3BotoStorage):
#     location = 'media'

AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
@deconstructible
class CustomS3BotoStorage(S3BotoStorage):

    def __init__(self, **kwargs):
    	super(CustomS3BotoStorage,self).__init__(**kwargs)
    	self.bucket_name = AWS_STORAGE_BUCKET_NAME
    	self.location = 'media'
    	self.querystring_auth=False