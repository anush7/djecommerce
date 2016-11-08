import os
from ConfigParser import RawConfigParser

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = RawConfigParser()
config.read(os.path.join(SETTINGS_DIR, 'config.cfg'))

DATABASES = {
    'default': {
        'ENGINE': config.get('local_db', 'ENGINE'),
        'NAME': config.get('local_db', 'NAME'),
        'USER': config.get('local_db', 'USER'),
        'PASSWORD': config.get('local_db', 'PASSWORD'),
        'HOST': config.get('local_db', 'HOST'),
        'PORT': config.get('local_db', 'PORT'),
    }
}
from access_settings import *

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR),'estatic_prod','media_root')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR),'estatic_prod','static_root')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'),)




