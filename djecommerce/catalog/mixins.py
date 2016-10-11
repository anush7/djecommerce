from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from functools import wraps

from django.http import Http404

def staff_required(export_func):
	def export_func_wrap(request, *args, **kwargs):
		if request.user.is_authenticated() and request.user.is_staff:
			return export_func(request, *args, **kwargs)
		return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
	export_func_wrap.__doc__ = export_func.__doc__
	export_func_wrap.__name__ = export_func.__name__
	return export_func_wrap

def admin_required(export_func):
	def export_func_wrap(request, *args, **kwargs):
		if request.user.is_authenticated() and request.user.is_admin:
			return export_func(request, *args, **kwargs)
		else:
			return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
	export_func_wrap.__doc__ = export_func.__doc__
	export_func_wrap.__name__ = export_func.__name__
	return export_func_wrap

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

class StaffRequiredMixin(object):
	@classmethod
	def as_view(self, *args, **kwargs):
		view = super(StaffRequiredMixin, self).as_view(*args, **kwargs)
		return login_required(view)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_staff:
			role_permissions = []
			map(lambda x: role_permissions.extend(x.permissions.values_list('codename',flat=True)), request.user.groups.all())
			print role_permissions
			if all(map(lambda x: x in role_permissions, self.permissions)) or request.user.is_admin:
				return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)
		# return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])
		return HttpResponseRedirect(reverse('user-access-denied'))


		# if request.user.is_staff:
		# 	return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)
		# else:
		# 	return HttpResponseRedirect(reverse('user_signin')+"?next="+request.META['PATH_INFO'])

class LoginRequiredMixin(object):
	@classmethod
	def as_view(self, *args, **kwargs):
		view = super(LoginRequiredMixin, self).as_view(*args, **kwargs)
		return login_required(view)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
