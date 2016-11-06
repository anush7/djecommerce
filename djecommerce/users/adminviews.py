import jwt
import json
from django.http import JsonResponse, Http404
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.paginator import InvalidPage, Paginator
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import Permission, Group
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import *
from django.views.generic.list import ListView
from users.utils import send_mg_email
from django.conf import settings

from catalog.models import Catalog, CatalogCategory
from carts.models import Tax
from catalog.forms import TaxForm
from orders.forms import ShippingForm, CurrencyForm
from orders.models import Shipping, Currency
from users.models import EcUser as User
from users.models import GroupDetails
from users.mixins import StaffRequiredMixin, StaffUpdateRequiredMixin, AdminRequiredMixin
from users.decorators import staff_required, staff_update_required


class StaffManagementView(AdminRequiredMixin, ListView):
	template_name = 'users/admin/user_management.html'
	paginate_by = 10

	def get_queryset(self):
		key = {'is_staff':True,'is_superuser':False}
		user_status = self.request.GET.get('s','A')
		if user_status == 'A':key['is_active'] = True
		else:key['is_active'] = False
		staffs = User.objects.filter(**key).order_by('first_name')
		return staffs

	def get_context_data(self, **kwargs):
	    context = super(StaffManagementView, self).get_context_data(**kwargs)
	    context['roles'] = Group.objects.all().order_by('name')
	    return context

	def paginate_queryset(self, queryset, page_size):
	    """
	    Paginate the queryset, if needed.
	    """
	    paginator = self.get_paginator(
	        queryset, page_size, orphans=self.get_paginate_orphans(),
	        allow_empty_first_page=self.get_allow_empty())
	    page_kwarg = self.page_kwarg
	    page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
	    try:
	        page_number = int(page)
	    except ValueError:
	        if page == 'last':
	            page_number = paginator.num_pages
	        else:
	            raise Http404(_("Page is not 'last', nor can it be converted to an int."))
	    try:
	        page = paginator.page(page_number)
	        return (paginator, page, page.object_list, page.has_other_pages())
	    except InvalidPage as e:
	    	try:
	    		page = paginator.page(page_number-1)
	    		return (paginator, page, page.object_list, page.has_other_pages())
	    	except:
		        raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
		            'page_number': page_number,
		            'message': str(e)
				})

	def get(self, request, *args, **kwargs):
		self.object_list = self.get_queryset()

		if request.is_ajax():
			html_data = {}
			staff_id = request.GET.get('staff_id')
			skey = request.GET.get('key')
			if staff_id:
				staff = User.objects.get(id=staff_id)
				if request.GET.get('status'):
					if request.GET.get('status','A') == 'A':staff.is_active = True
					else: staff.is_active = False
					staff.save()
					html_data['status'] = 1
				elif request.GET.get('role_id'):
					try:
						grp = Group.objects.get(id=int(request.GET.get('role_id')))
						staff.groups.clear()
						staff.groups.add(grp)
						return JsonResponse({'status':1})
					except:
						return JsonResponse({'status':0})
				elif request.GET.get('delete'):
					staff.delete()

			if skey:
				self.object_list = self.get_queryset().filter(
					Q(first_name__startswith=skey)|Q(last_name__startswith=skey)|Q(email__startswith=skey)
				)

			context = self.get_context_data(**kwargs)
			html_data['html'] = render_to_string('users/admin/part_staff_users.html',context,context_instance=RequestContext(request))
			return JsonResponse(html_data)

		context = self.get_context_data(**kwargs)
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		self.object_list = self.get_queryset()
		
		if request.is_ajax():
			html_data = {}

			context = self.get_context_data(**kwargs)
			html_data['html'] = render_to_string('users/admin/part_staff_users.html',context,context_instance=RequestContext(request))
			return JsonResponse(html_data)

		messages.error(request, "Please select a category")
		messages.success(request, "Import Complete")
		context = self.get_context_data(**kwargs)
		return render(request, self.template_name, {})


class StaffRoleDeleteView(AdminRequiredMixin, View):

	def post(self, request, *args, **kwargs):
		data = {}
		roleId = request.POST.get('role_id')
		try:
			if roleId:
				Group.objects.get(id=roleId).delete()
				return JsonResponse({'status':1})
		except:pass
		return JsonResponse({'status':0})

class StaffInviteView(AdminRequiredMixin, View):

	def post(self, request, *args, **kwargs):
		invite_emails = request.POST.getlist('invite_email')
		sign_up_url = 'http://127.0.0.1:8000/signup'
		from_name = request.user.first_name

		subject = 'Staff Sign up Invite'
		body = 'Hi, <br><br>'
		body += 'You have been invited to sign up as staff by %s<br><br>' % request.user.first_name
		body += 'Click the link below to sign up<br>'

		for email in request.POST.getlist('invite_email',[]):
			if email:
				encoded = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256')
				staff_sign_up_url = sign_up_url+'?staff=%s' % encoded
				body += '<a target="_blank" href="%s">Staff Sign Up</a><br>' % staff_sign_up_url
				send_mg_email(subject, body, from_name=from_name, to_email=[email])

		return JsonResponse({'status':1})


class StaffRoleView(AdminRequiredMixin, TemplateView):
    template_name = 'users/admin/permissions.html'

    def get_context_data(self, **kwargs):
        context = super(StaffRoleView, self).get_context_data(**kwargs)
        context['parent_cats'] = CatalogCategory.objects.filter(parent__isnull=True).order_by('name')
        return context

    def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)

		if request.is_ajax() and request.GET.get('delete') and request.GET.get('role_id'):
			data = {}
			try:
				role = Group.objects.get(id=int(request.GET.get('role_id')))
				role.delete()
				data['status'] = 1
			except:data['status'] = 0
			return JsonResponse(data)

		if kwargs.get('pk'):
			role = Group.objects.get(id=kwargs['pk'])
			context['role'] = role
			context['permissions'] = role.permissions.values_list('codename', flat=True)
		
		return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
    	context = self.get_context_data(**kwargs)

    	perms = request.POST.getlist('perms',[])
    	pcats = request.POST.getlist('parent_category',[])
    	grp_id = request.POST.get('grp_id',False)
    	grp_name = request.POST.get('role_name',False)

    	if grp_id:
    		grp = Group.objects.get(id=grp_id)
    		grp.name = grp_name
    		grp.save()
    		grp.permissions.clear()
    		grp.details.categories.clear()
    		messages.success(request, "Role updated successfully!")
    	else:
    		grp = Group.objects.create(name=grp_name)
    		GroupDetails.objects.create(group=grp)
    		messages.success(request, "Role added successfully!")

    	grp.permissions = Permission.objects.filter(codename__in=perms)
    	grp.details.categories = CatalogCategory.objects.filter(id__in=pcats)

    	context['role'] = grp
    	context['permissions'] = grp.permissions.values_list('codename', flat=True)
    	return HttpResponseRedirect(reverse('staff_management'))

        # return render(request, self.template_name, context)

"""###############################Tax Views############################"""

class TaxListView(AdminRequiredMixin, ListView):
    template_name = 'users/admin/tax_list.html'

    def get_queryset(self):
        return Tax.objects.all().order_by('name')

class TaxFormView(AdminRequiredMixin, FormView):
    template_name = 'users/admin/tax_form.html'
    form_class = TaxForm
    success_url = reverse_lazy('tax_list')

    def get_form_kwargs(self):
        kwargs = super(TaxFormView, self).get_form_kwargs()
        if self.kwargs.get('pk'):
            tax = Tax.objects.get(id=self.kwargs.get('pk'))
            kwargs.update({'instance': tax})
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

class TaxDeleteView(AdminRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            data = {}
            try:
                tax = Tax.objects.get(id=kwargs['pk'])
                tax.delete()
                data['status'] = 1
            except:data['status'] = 0
            return JsonResponse(data)
        else:
            raise Http404

"""###############################Shipping Settings############################"""


class ShippingFormView(AdminRequiredMixin, FormView):
    template_name = 'users/admin/shipping_form.html'
    form_class = ShippingForm
    success_url = reverse_lazy('shipping_settings')

    def get_form_kwargs(self):
        kwargs = super(ShippingFormView, self).get_form_kwargs()
        try:
            shipObj = Shipping.objects.get(id=1)
            kwargs.update({'instance': shipObj})
        except:pass
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            messages.success(request, "Shipping Rate Successfully updated")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class CurrencyFormView(AdminRequiredMixin, FormView):
    template_name = 'users/admin/currency_form.html'
    form_class = CurrencyForm
    success_url = reverse_lazy('currency_settings')

    def get_form_kwargs(self):
        kwargs = super(CurrencyFormView, self).get_form_kwargs()
        try:
            currObj = Currency.objects.get(id=1)
            kwargs.update({'instance': currObj})
        except:pass
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            messages.success(request, "Currency Successfully updated")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)