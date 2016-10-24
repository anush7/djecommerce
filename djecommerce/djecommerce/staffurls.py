from django.conf.urls import include, url
from users.views import LowStockProducts
from users.staffviews import ProcessOrderView

urlpatterns = [

	url(r'^', include('catalog.staffurls')),
	url(r'^', include('products.staffurls')),
	url(r'^low-stock-products$', LowStockProducts.as_view(), name='low-stock-products'),
	url(r'^process-order$', ProcessOrderView.as_view(), name='process-order'),
]