from django.conf.urls import include, url
from users.views import LowStockProducts

urlpatterns = [

	url(r'^', include('catalog.staffurls')),
	url(r'^', include('products.staffurls')),
	url(r'^low-stock-products$', LowStockProducts.as_view(), name='low-stock-products'),
]