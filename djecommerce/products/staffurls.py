from django.conf.urls import include, url
from products import staffviews


urlpatterns = [
	
	#products
	url(r'^products$', staffviews.ProductListView.as_view(), name='staff-product-list'),
	url(r'^products/ajax-list$', staffviews.ajax_product_list, name='staff-ajax-product-list'),
	url(r'^products/add$', staffviews.ProductCreateView.as_view(), name='staff-product-add'),
	url(r'^products/edit/(?P<pk>\d+)$', staffviews.ProductUpdateView.as_view(), name='staff-product-edit'),
	url(r'^products/delete/(?P<pk>\d+)$', staffviews.delete_product, name='staff-product-delete'),
	url(r'^products/(?P<pk>\d+)$', staffviews.ProductDetailView.as_view(), name='staff-product-detail'),
	url(r'^products/load_subcats$', staffviews.get_sub_cats, name='staff-ajax-load-prod-subcats'),
	# url(r'^products/load_attributes$', staffviews.get_attributes, name='staff-ajax-load-prod-attributes'),
	# url(r'^products/load_attribute_values$', staffviews.get_attribute_values, name='staff-ajax-load-attribute-values'),

	#variants
	url(r'^products/(?P<pid>\d+)/variants$', staffviews.VariantListView.as_view(), name='staff-variant-list'),
	url(r'^products/(?P<pid>\d+)/variants/add$', staffviews.VariantCreateView.as_view(), name='staff-variant-add'),
	url(r'^products/(?P<pid>\d+)/variants/(?P<pk>\d+)$', staffviews.VariantUpdateView.as_view(), name='staff-variant-update'),
	url(r'^products/(?P<pid>\d+)/variants/delete$', staffviews.VariantDeleteView, name='staff-variant-delete'),

	#stocks
	url(r'^products/(?P<pid>\d+)/stocks$', staffviews.StockListView.as_view(), name='staff-stock-list'),
	url(r'^products/(?P<pid>\d+)/stocks/add$', staffviews.StockCreateView.as_view(), name='staff-stock-add'),
	url(r'^products/(?P<pid>\d+)/stocks/(?P<pk>\d+)$', staffviews.StockUpdateView.as_view(), name='staff-stock-update'),
	url(r'^products/(?P<pid>\d+)/stocks/delete$', staffviews.StockDeleteView, name='staff-stock-delete'),

	#Images
	url(r'^products/(?P<pid>\d+)/images$', staffviews.ProductImageView.as_view(), name='staff-image-list'),
	url(r'^products/(?P<pid>\d+)/images/add$', staffviews.ProductImageCreateView.as_view(), name='staff-image-add'),
	url(r'^products/(?P<pid>\d+)/images/(?P<pk>\d+)$', staffviews.ProductImageUpdateView.as_view(), name='staff-image-update'),
	url(r'^products/(?P<pid>\d+)/images/delete$', staffviews.ProductImageDeleteView, name='staff-image-delete'),



]















