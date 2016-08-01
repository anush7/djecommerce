from django.conf.urls import include, url
from products import views


urlpatterns = [
	
	url(r'^$', views.ProductListView.as_view(), name='product-list'),
	url(r'^products/ajax-list$', views.ajax_product_list, name='ajax-product-list'),
	url(r'^product/(?P<pk>\d+)$', views.ProductDetailView.as_view(), name='product-detail'),

]















