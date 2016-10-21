from django.core.urlresolvers import reverse

role_permissions = ['access_catalog','access_catalogcategory','access_tax','access_product','access_productattribute','access_import','access_export']

modulesData = {
	'catalog': reverse('staff-catalog-list'),
	'category': reverse('staff-category-list'),
	'tax': reverse('staff-tax-list'),
	'product': reverse('staff-product-list'),
	'attribute': reverse('staff-attribute-list'),
	'import': reverse('staff-products-import'),
	'export': reverse('staff-products-export'),
}

updatePermissionType = {
	'change_product':'all', 'change_owned_product':'owned',
	'change_productattribute':'all','change_owned_productattribute':'owned',
	'change_catalogcategory':'all','change_owned_catalogcategory':'owned',
	'change_catalog':'all','change_owned_catalog':'owned',
	'change_tax':'all','change_owned_tax':'owned'
}

month_count = {
	'this_week': 7,
	'last_week': 7,
	'this_quarter': 3,
	'last_quarter': 3,
	'this_year': 12,
	'last_year': 12
}