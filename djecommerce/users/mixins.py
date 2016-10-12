import json
from django.http import Http404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

class StaffRequiredMixin(object):

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_staff:
			role_permissions = []
			map(lambda x: role_permissions.extend(x.permissions.values_list('codename',flat=True)), request.user.groups.all())
			if request.user.is_admin or all(map(lambda x: x in role_permissions, self.permissions)):
				return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)
		return HttpResponseRedirect(reverse('user-access-denied'))


class StaffUpdateRequiredMixin(object):

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		from users.constants import updatePermissionType
		if not request.user.is_staff:
			return HttpResponseRedirect(reverse('user-access-denied'))
		if request.user.is_admin:
			return super(StaffUpdateRequiredMixin, self).dispatch(request, *args, **kwargs)

		role_permissions = []
		grant_access = False
		map(
			lambda x:
				role_permissions.extend(
					x.permissions.filter(codename__in=self.permissions)\
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
			return super(StaffUpdateRequiredMixin, self).dispatch(request, *args, **kwargs)
		return HttpResponseRedirect(reverse('user-access-denied'))

class LoginRequiredMixin(object):
	
	@classmethod
	def as_view(self, *args, **kwargs):
		view = super(LoginRequiredMixin, self).as_view(*args, **kwargs)
		return login_required(view)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

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
