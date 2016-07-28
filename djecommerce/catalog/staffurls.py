from django.conf.urls import include, url
from catalog import staffviews


urlpatterns = [
	
	#Catalog staff urls
	url(r'^catalog$', staffviews.CatalogListView.as_view(), name='staff-catalog-list'),
	url(r'^catalog/ajax-list$', staffviews.ajax_catalog_list, name='staff-ajax-catalog-list'),
	url(r'^catalog/add$', staffviews.CatalogCreateView.as_view(), name='staff-catalog-add'),
	url(r'^catalog/edit/(?P<pk>\d+)$', staffviews.CatalogUpdateView.as_view(), name='staff-catalog-edit'),
	url(r'^catalog/delete/(?P<pk>\d+)$', staffviews.delete_catalog, name='catalog-delete'),
	url(r'^catalog/status/(?P<pk>\d+)$', staffviews.change_catalog_status, name='catalog-status'),

	#Category staff urls
	url(r'^category$', staffviews.CategoryListView.as_view(), name='staff-category-list'),
	url(r'^category/ajax-list$', staffviews.ajax_category_list, name='staff-ajax-category-list'),
	url(r'^category/add$', staffviews.CategoryCreateView.as_view(), name='staff-category-add'),
	url(r'^category/edit/(?P<pk>\d+)$', staffviews.CategoryUpdateView.as_view(), name='staff-category-edit'),
	url(r'^category/delete/(?P<pk>\d+)$', staffviews.delete_category, name='staff-category-delete'),
	url(r'^category/status/(?P<pk>\d+)$', staffviews.change_category_status, name='staff-category-status'),

	#Attributes staff urls
	url(r'^attribute$', staffviews.AttributeListView.as_view(), name='staff-attribute-list'),
	url(r'^attribute/ajax-list$', staffviews.ajax_attribute_list, name='staff-ajax-attribute-list'),
	url(r'^attribute/add$', staffviews.AttributeCreateView.as_view(), name='staff-attribute-add'),
	url(r'^attribute/edit/(?P<pk>\d+)$', staffviews.AttributeUpdateView.as_view(), name='staff-attribute-edit'),
	url(r'^attribute/delete/(?P<pk>\d+)$', staffviews.delete_attribute, name='staff-attribute-delete'),
	url(r'^attribute/status/(?P<pk>\d+)$', staffviews.change_attribute_status, name='attribute-status'),
	url(r'^attribute/form_subcats$', staffviews.get_sub_cats, name='staff-ajax-load-subcats'),
	url(r'^attribute/list_subcats$', staffviews.get_list_sub_cats, name='staff-ajax-load-list-subcats'),

	#Tax urls
	url(r'^tax$', staffviews.TaxListView.as_view(), name='staff-tax-list'),
	url(r'^tax/add$', staffviews.TaxFormView.as_view(), name='staff-tax-add'),
	url(r'^tax/(?P<pk>\d+)$', staffviews.TaxFormView.as_view(), name='staff-tax-update'),
	url(r'^tax/delete/(?P<pk>\d+)$', staffviews.TaxDeleteView.as_view(), name='staff-tax-delete'),




	# url(r'^image/add$', views.upload_article_images, name='product-upload-images'),
	# url(r'^image/delete$', views.delete_article_image, name='product-delete-image'),





	# url(r'^category/add$', views.ArticleCategoryCreateView.as_view(), name='product-category-add'),
	# url(r'^category/edit/(?P<pk>\d+)$', views.ArticleCategoryUpdateView.as_view(), name='product-category-edit'),
	# url(r'^category/delete/(?P<pk>\d+)$', views.delete_category, name='product-category-delete'),

	# url(r'^import$', ImportArticles.as_view(), name='import-articles'),
	# url(r'^export$', ExportArticles.as_view(), name='export-articles'),
	# url(r'^import-file$', views.import_file, name='import-articles-file'),
	# url(r'^export-file$', views.export_file, name='export-articles-file'),
]















