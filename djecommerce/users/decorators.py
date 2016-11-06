import json
from functools import wraps
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.models import Permission, Group

def staff_required(permissions):
	def staff_required_dec(view_func):
		def wrapped_view_func(request, *args, **kwargs):
			if request.user.is_authenticated():
				if request.user.is_staff:
					if all(map(lambda perm: request.user.has_perm(perm), permissions)):
						return view_func(request, *args, **kwargs)
					else:
						if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
						return HttpResponseRedirect(reverse('staff-dashboard'))	
				else:
					if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
					return HttpResponseRedirect(reverse('product-list'))
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
		wrapped_view_func.__doc__ = view_func.__doc__
		wrapped_view_func.__name__ = view_func.__name__
		return wrapped_view_func
	return staff_required_dec

def staff_update_required(permissions):
	def staff_update_required_dec(view_func):
		def wrapped_view_func(request, *args, **kwargs):
			from users.constants import updatePermissionType
			if request.user.is_authenticated():
				if request.user.is_admin: return view_func(request, *args, **kwargs)
				if request.user.is_staff:
					grant_access = False
					role_permissions = Permission.objects\
										.filter(codename__in=permissions,group__user=request.user)\
										.values_list('codename',flat=True)

					for per in role_permissions:
						if 'owned' in per:
							if self.get_object().created_by == request.user:
								grant_access = True
						else:
							grant_access = True
					if grant_access:
						return view_func(request, *args, **kwargs)
					else:
						if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
						return HttpResponseRedirect(reverse('staff-dashboard'))	
				else:
					if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
					return HttpResponseRedirect(reverse('product-list'))
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
		wrapped_view_func.__doc__ = view_func.__doc__
		wrapped_view_func.__name__ = view_func.__name__
		return wrapped_view_func
	return staff_update_required_dec

def only_staff_required(view_func):
	def wrapped_view_func(request, *args, **kwargs):
		if request.user.is_authenticated():
			if request.user.is_staff or request.user.is_admin:
				return view_func(request, *args, **kwargs)
			else:
				if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
				return HttpResponseRedirect(reverse('product-list'))	
		else:
			if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
	wrapped_view_func.__doc__ = view_func.__doc__
	wrapped_view_func.__name__ = view_func.__name__
	return wrapped_view_func

def admin_required(view_func):
	def wrapped_view_func(request, *args, **kwargs):
		if request.user.is_authenticated():
			if request.user.is_admin:
				return view_func(request, *args, **kwargs)
			else:
				if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
				return HttpResponseRedirect(reverse('product-list'))	
		else:
			if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
	wrapped_view_func.__doc__ = view_func.__doc__
	wrapped_view_func.__name__ = view_func.__name__
	return wrapped_view_func












################################old###############################################


# def staff_required2(permissions):
# 	def staff_required_dec(view_func):
# 		def wrapped_view_func(request, *args, **kwargs):
# 			if request.user.is_authenticated():
# 				if request.user.is_staff:
# 					role_permissions = []
# 					map(lambda x: role_permissions.extend(x.permissions.values_list('codename',flat=True)), request.user.groups.all())
# 					if request.user.is_admin or all(map(lambda x: x in role_permissions, permissions)):
# 						return view_func(request, *args, **kwargs)
# 					else:
# 						if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
# 						return HttpResponseRedirect(reverse('staff-dashboard'))	
# 				else:
# 					if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
# 					return HttpResponseRedirect(reverse('product-list'))
# 			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
# 		wrapped_view_func.__doc__ = view_func.__doc__
# 		wrapped_view_func.__name__ = view_func.__name__
# 		return wrapped_view_func
# 	return staff_required_dec

# def staff_update_required2(permissions):
# 	def staff_update_required_dec(view_func):
# 		def wrapped_view_func(request, *args, **kwargs):
# 			from users.constants import updatePermissionType
# 			if request.user.is_authenticated():
# 				if request.user.is_admin: return view_func(request, *args, **kwargs)
# 				if request.user.is_staff:
# 					role_permissions = []
# 					grant_access = False
# 					map(
# 						lambda x:
# 							role_permissions.extend(
# 								x.permissions.filter(codename__in=permissions)\
# 								.values_list('codename',flat=True)
# 							),
# 						request.user.groups.all()
# 					)
# 					for per in role_permissions:
# 						if updatePermissionType[per] == 'owned':
# 							if self.get_object().created_by == request.user:
# 								grant_access = True
# 						elif updatePermissionType[per] == 'all':
# 							grant_access = True
# 					if grant_access:
# 						return view_func(request, *args, **kwargs)
# 					else:
# 						if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
# 						return HttpResponseRedirect(reverse('staff-dashboard'))	
# 				else:
# 					if request.is_ajax():return HttpResponse(json.dumps({'error':'Access denied!'}))
# 					return HttpResponseRedirect(reverse('product-list'))
# 			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
# 		wrapped_view_func.__doc__ = view_func.__doc__
# 		wrapped_view_func.__name__ = view_func.__name__
# 		return wrapped_view_func
# 	return staff_update_required_dec



# def user_passes_test(test_func):
# 	def decorator(view_func):
# 		def wrapped_view_func(request, *args, **kwargs):
# 			if test_func(request, *args, **kwargs):
# 				return view_func(request, *args, **kwargs)
# 			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
# 		return wrapped_view_func
# 	return decorator