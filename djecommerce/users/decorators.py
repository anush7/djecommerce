import json
from functools import wraps
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse


def staff_update_required(permissions):
	def staff_update_required_dec(view_func):
		def wrapped_view_func(request, *args, **kwargs):
			if request.user.is_authenticated():
				if request.user.is_admin: return view_func(request, *args, **kwargs)
				if request.user.is_staff:
					role_permissions = []
					grant_access = False
					map(
						lambda x:
							role_permissions.extend(
								x.permissions.filter(codename__in=permissions)\
								.values_list('codename',flat=True)
							),
						request.user.groups.all()
					)
					for per in role_permissions:
						if updatePermissionType[per] == 'owned':
							if self.get_object().created_by == request.user:
								grant_access = True
						elif updatePermissionType[per] == 'all':
							grant_access = True
					if grant_access:
						return view_func(request, *args, **kwargs)
					else:
						if request.is_ajax:return HttpResponse(json.dumps({'error':'Access denied!'}))
						return HttpResponseRedirect(reverse('staff-dashboard'))	
				else:
					if request.is_ajax:return HttpResponse(json.dumps({'error':'Access denied!'}))
					return HttpResponseRedirect(reverse('product-list'))
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
		wrapped_view_func.__doc__ = view_func.__doc__
		wrapped_view_func.__name__ = view_func.__name__
		return wrapped_view_func
	return staff_update_required_dec