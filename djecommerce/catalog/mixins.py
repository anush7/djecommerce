import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from functools import wraps

from django.http import Http404

def user_passes_test(test_func):
	def decorator(view_func):
		def wrapped_view_func(request, *args, **kwargs):
			if test_func(request, *args, **kwargs):
				return view_func(request, *args, **kwargs)
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
		return wrapped_view_func
	return decorator

def staff_required(permissions):
	def staff_required_dec(view_func):
		def wrapped_view_func(request, *args, **kwargs):
			if request.user.is_authenticated():
				if request.user.is_staff:
					role_permissions = []
					map(lambda x: role_permissions.extend(x.permissions.values_list('codename',flat=True)), request.user.groups.all())
					if request.user.is_admin or all(map(lambda x: x in role_permissions, permissions)):
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
	return staff_required_dec

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






def admin_required(permissions):
	def admin_required_dec(view_func):
		def wrapped_view_func(request, *args, **kwargs):
			if request.user.is_authenticated():
				if request.user.is_admin:
					return view_func(request, *args, **kwargs)
				else:
					if request.is_ajax:return HttpResponse(json.dumps({'error':'Access denied!'}))
					return HttpResponseRedirect(reverse('staff-dashboard'))	
			else:
				if request.is_ajax:return HttpResponse(json.dumps({'error':'Access denied!'}))
				return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
		wrapped_view_func.__doc__ = view_func.__doc__
		wrapped_view_func.__name__ = view_func.__name__
		return wrapped_view_func
	return admin_required_dec

class StaffRequiredMixin(object):

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_staff:
			role_permissions = []
			map(lambda x: role_permissions.extend(x.permissions.values_list('codename',flat=True)), request.user.groups.all())
			if request.user.is_admin or all(map(lambda x: x in role_permissions, self.permissions)):
				return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)
		return HttpResponseRedirect(reverse('user-access-denied'))


class AdminRequiredMixin(object):
	@classmethod
	def as_view(self, *args, **kwargs):
		view = super(AdminRequiredMixin, self).as_view(*args, **kwargs)
		return login_required(view)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_admin:
			return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)
		else:
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])




class LoginRequiredMixin(object):
	@classmethod
	def as_view(self, *args, **kwargs):
		view = super(LoginRequiredMixin, self).as_view(*args, **kwargs)
		return login_required(view)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
