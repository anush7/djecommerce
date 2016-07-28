from django.conf.urls import include, url
from products import views


urlpatterns = [
	
	#products
	url(r'^$', views.ProductListView.as_view(), name='product-list'),
	url(r'^product/(?P<pk>\d+)$', views.ProductDetailView.as_view(), name='product-detail'),

	# url(r'^product/get-variant-images$', views.VariantImageView.as_view(), name='product-variant-images'),
]















