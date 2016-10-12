import json
from django.http import Http404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

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


class StaffImportRequiredMixin(object):

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_staff:
			return HttpResponseRedirect(reverse('user-access-denied'))
		if request.user.is_admin:
			return super(StaffImportRequiredMixin, self).dispatch(request, *args, **kwargs)

		role_permissions = set([])
		for role in request.user.groups.all():
			if role.details.is_import:role_permissions.add('import')
			if role.details.is_export:role_permissions.add('export')

		if self.permission and self.permission[0] in role_permissions:
			return super(StaffImportRequiredMixin, self).dispatch(request, *args, **kwargs)
		else:
			return HttpResponseRedirect(reverse('user-access-denied'))


