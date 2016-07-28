from django.conf import settings
from django.conf.urls import include, url
from users import views

urlpatterns = [
	url(r'^check-username-email$', views.check_username_email, name='check-username-email'),
]