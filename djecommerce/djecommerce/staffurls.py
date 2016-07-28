from django.conf.urls import include, url
from django.conf import settings

urlpatterns = [

	url(r'^', include('catalog.staffurls')),
	url(r'^', include('products.staffurls')),
	
]