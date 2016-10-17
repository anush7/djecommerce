from django.conf.urls import include, url

urlpatterns = [

	url(r'^', include('catalog.staffurls')),
	url(r'^', include('products.staffurls')),
	
]