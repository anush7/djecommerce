import os
from ConfigParser import RawConfigParser

DEBUG = False
ALLOWED_HOSTS = ['*']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = RawConfigParser()
config.read(os.path.join(SETTINGS_DIR, 'config.cfg'))

DATABASES = {
    'default': {
        'ENGINE': config.get('prod_db', 'ENGINE'),
        'NAME': config.get('prod_db', 'NAME'),
        'USER': config.get('prod_db', 'USER'),
        'PASSWORD': config.get('prod_db', 'PASSWORD'),
        'HOST': config.get('prod_db', 'HOST'),
        'PORT': config.get('prod_db', 'PORT'),
    }
}
from access_settings import *

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'),)

STATICFILES_STORAGE = 'djecommerce.s3utils.StaticRootS3BotoStorage'
STATICFILES_LOCATION = 'static'
STATIC_URL = "http://%s.s3.amazonaws.com/%s/" % (AWS_STORAGE_BUCKET_NAME, STATICFILES_LOCATION)

DEFAULT_FILE_STORAGE = 'djecommerce.s3utils.MediaRootS3BotoStorage'
MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "http://%s.s3.amazonaws.com/%s/" % (AWS_STORAGE_BUCKET_NAME, MEDIAFILES_LOCATION)





