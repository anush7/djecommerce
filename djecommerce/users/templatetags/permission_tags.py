from django import template
register = template.Library()
from users.constants import *

@register.inclusion_tag('staff_nav_bar_li.html')
def get_staff_nav_bar(user):
	modules = []
	# map(
	# 	lambda x:
	# 		modules.extend(
	# 			[per.split('access_')[1] for per in x.permissions.filter(codename__startswith='access')\
	# 			.values_list('codename',flat=True) if per in role_permissions]
	# 		), 
	# 	user.groups.all()
	# )
	for x in user.groups.all():
		modules.extend(
			[per.split('access_')[1] for per in x.permissions.filter(codename__startswith='access')\
			.values_list('codename',flat=True) if per in role_permissions]
		)

	for i,mod in enumerate(modules):
		if mod == 'catalogcategory':
			modules[i] = 'category'
		elif mod == 'productattribute':
			modules[i] = 'attribute'

	modules = {mod:modulesData[mod] for mod in modules}
	return {'modules':modules}


@register.simple_tag
def check_permission(user, permission):
	if not user.is_staff: return False
	if user.is_admin:return True

	role_permissions = []
	map(
		lambda x:
			role_permissions.extend(
				x.permissions.values_list('codename',flat=True)
			),
		user.groups.all()
	)
	grant_access = False
	if permission in role_permissions:
		grant_access = True

	return grant_access


@register.simple_tag
def check_update_permission(user, created_by, permissions):
	if not user.is_staff:return False
	if user.is_admin:return True

	required_perms = [p.strip() for p in permissions.split(',')]
	role_permissions = []
	map(
		lambda x:
			role_permissions.extend(
				x.permissions.filter(codename__in=required_perms)\
				.values_list('codename',flat=True)
			),
		user.groups.all()
	)
	grant_access = False
	for per in role_permissions:
		if updatePermissionType[per] == 'owned':
			if user == created_by:
				grant_access = True
		elif updatePermissionType[per] == 'all':
			grant_access = True

	return grant_access





































