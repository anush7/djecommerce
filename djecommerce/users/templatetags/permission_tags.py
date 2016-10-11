from django import template
register = template.Library()
from django.core.urlresolvers import reverse

role_permissions = ['access_catalog','access_catalogcategory','access_tax','access_product','access_productattribute']
modulesData = {
	'catalog': reverse('staff-catalog-list'),
	'category': reverse('staff-category-list'),
	'tax': reverse('staff-tax-list'),
	'product': reverse('staff-product-list'),
	'attribute': reverse('staff-attribute-list') 
}

@register.inclusion_tag('staff_nav_bar_li.html')
def get_staff_nav_bar(user):
	modules = []
	map(
		lambda x:
			modules.extend(
				[per.split('access_')[1] for per in x.permissions.filter(codename__startswith='access')\
				.values_list('codename',flat=True) if per in role_permissions]
			), 
		user.groups.all()
	)
	for i,mod in enumerate(modules):
		if mod == 'catalogcategory':
			modules[i] = 'category'
		elif mod == 'productattribute':
			modules[i] = 'attribute'

	modules = {mod:modulesData[mod] for mod in modules}
	return {'modules':modules}

