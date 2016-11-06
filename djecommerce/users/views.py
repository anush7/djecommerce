import re
import json
import uuid
import requests
import jwt
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib import messages
from django.db.models import F, Count, Sum, Case, When, Q, Value, IntegerField
from django.shortcuts import render, render_to_response, get_list_or_404,get_object_or_404
from django.core.paginator import InvalidPage, Paginator
from django.template.loader import render_to_string
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from django.core.mail import send_mail
from django.conf import settings
from users.forms import UserSignUpForm, UserProfileForm
from users.models import EcUser as User
from users.models import GroupDetails
from django.contrib.auth.decorators import login_required
from orders.models import UserAddress, Order
from orders.forms import UserAddressForm
from users.mixins import AdminRequiredMixin, LoginRequiredMixin, OnlyStaffRequiredMixin
from catalog.models import Catalog, CatalogCategory
from products.models import Product, ProductVariant, Stock
from users.utils import send_mg_email
from collections import OrderedDict
from users.decorators import only_staff_required

@only_staff_required
def dashboard(request,template='users/staff/dashboard.html'):
	data={}
	return render(request, template, data)

def user_signup(request, template='users/signup.html'):
	data = {}
	if request.method == 'POST':
		form = UserSignUpForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(
				email=form.cleaned_data['email'],
				password=form.cleaned_data['password'],
				username=form.cleaned_data['username'],
				first_name=form.cleaned_data['first_name'],
				last_name=form.cleaned_data['last_name'],
			)
			if request.POST.get('staff',False):
				try:
					email = jwt.decode(request.POST.get('staff'), settings.SECRET_KEY , algorithms=['HS256'])['email']
					if user.email == email:
						user.is_staff = True
						user.save()
				except:pass
			user=authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
			login(request, user)
			try:next_url = request.GET['next']
			except:
				try:next_url = request.POST['next']
				except:next_url = reverse('product-list')
			return HttpResponseRedirect(next_url)
	else:
		form = UserSignUpForm()
		if request.GET.get('staff',False):
			try:
				encodedData = request.GET.get('staff')
				email = jwt.decode(encodedData, settings.SECRET_KEY , algorithms=['HS256'])['email']
				form = UserSignUpForm(initial={'email': email})
				form.fields["email"].widget.attrs.update({'disabled': True})
				data['staff'] = encodedData
			except:form = UserSignUpForm()
	data['form'] = form
	return render(request, template, data)

def user_signin(request, template='users/signin.html'):
	if request.method == 'POST':
		data = {}
		if request.POST.get('email',False) and request.POST.get('password',False):
			try:
				user = User.objects.get(email__iexact=request.POST['email'])
			except User.DoesNotExist:
				try:
					user = User.objects.get(username__iexact=request.POST['email'])
				except:
					return render(request, template, {"error":"Sorry, we don't recognize this email"})
			try:
				user=authenticate(username=request.POST['email'], password=request.POST['password'])
				if user:
					login(request, user)
					try:next_url = request.GET['next']
					except:
						try:next_url = request.POST['next']
						except:next_url = reverse('product-list')
					return HttpResponseRedirect(next_url)
			except:pass
			data = {"error":"The email and password you entered don't match."}
		else:data = {"error":"Please enter your email and password."}
		return render(request, template, data)
	return render(request, template, {'error':False})

def change_password(request):
	data={}
	if request.POST:
		if request.POST.get('old',False) and request.POST.get('new',False) and request.POST.get('confirm',False):
			if request.POST.get('new',False) == request.POST.get('confirm',False):
				if request.user.check_password(request.POST['old']):
					username = request.user.username
					request.user.set_password(request.POST['new'])
					request.user.save()
					user=authenticate(username=username, password=request.POST['new'])
					login(request, user)
					data['msg'] = 'Password Reset Successful!'
				else:data['msg'] = 'Please enter your correct password!'
			else:data['msg'] = 'New passwords do not match!'
		else:data['msg'] = 'Please enter all fields!'
		return HttpResponse(json.dumps(data))
	return render(request, 'users/change-password.html')

def forgot_password(request, template="users/forgot-password.html"):
	data={}
	if request.POST:
		if request.POST.get('email',False):
			try:
				email_data = {}
				user = User.objects.get(email=request.POST.get('email'))
				from_email = settings.EMAIL_HOST_USER
				to_email = [user.email]
				if not user.uuid:
					user.uuid = str(uuid.uuid4()).replace('-','')
					user.save()
				encoded = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm='HS256')
				email_data['user'] = user
				email_data['reset_link'] = 'http://localhost:8000/reset-password/?code='+encoded
				html_content = body = render_to_string('users/reset-email.html',email_data,context_instance=RequestContext(request))
				subject = 'Password Reset Link - Ecommerce App'
				send_mg_email(subject, body, to_email=[user.email])
				data['msg'] = 'Please check your email for password rest link'
			except:
				import sys
				print sys.exc_info()
				data['msg'] = 'Sorry, we don\'t recognize this email address'
		else:
			data['msg'] = 'Please enter your registered email address'
	return render(request, template, {'data': data})

def reset_password(request, template="users/reset-password.html"):
	data={}
	if request.POST:
		if request.POST.get('pass1',False) and request.POST.get('pass2',False):
			try:
				code = request.POST.get('code',False)
				email = jwt.decode(code, settings.SECRET_KEY , algorithms=['HS256'])['email']
				user = User.objects.get(email=email)
				user.set_password(request.POST.get('pass1'))
				user.save()
				data['msg'] = 'Password reset successful'
			except:
				data['msg'] = 'Oops no able to process your request!'
		else:
			data['msg'] = 'Please enter both the fields'
		return HttpResponse(json.dumps(data))
	else:
		code = request.GET.get('code',False)
		if code:
			try:
				email = jwt.decode(code, settings.SECRET_KEY , algorithms=['HS256'])['email']
				user = User.objects.get(email=email)
				data['code'] = code
			except:data['msg'] = 'password reset Url expired'
		else:data['msg'] = 'Invalid password reset Url'
	return render(request, template, {'data': data})


def check_username_email(request):
	data={}
	val = request.GET.get('q',False)
	action = request.GET.get('action',False)
	if val:
		if action == 'email':
			try:
				if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$", val) != None:
					user = User.objects.get(email__iexact=val)
				else:
					data['msg'] = 'Please enter correct email.'			
			except:
				return HttpResponse(json.dumps({'status':1}))
		else:
			try:
				user = User.objects.get(username__iexact=val)
				data['msg'] = 'Username not available.'
			except:
				return HttpResponse(json.dumps({'status':1}))
		data['status'] = 0
	else:
		data['status'] = 0
	return HttpResponse(json.dumps(data))


class UserAddressListView(LoginRequiredMixin, ListView):
    template_name = 'users/addresses.html'

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

class UserAddressCreateView(LoginRequiredMixin, CreateView):
	form_class = UserAddressForm
	template_name = "users/add_address.html"

	def get_success_url(self, *args, **kwargs):
		return reverse("user_address_list")

	def form_valid(self, form, *args, **kwargs):
		form.instance.user = self.request.user
		if form.instance.type == 'billing':
			if not UserAddress.objects.filter(user=self.request.user,type='billing').exists():
				form.instance.default=True
		elif form.instance.type == 'shipping':
			if not UserAddress.objects.filter(user=self.request.user,type='shipping').exists():
				form.instance.default=True
		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

class UserAddressUpdateView(LoginRequiredMixin, UpdateView):
	model = UserAddress
	form_class = UserAddressForm
	template_name = "users/add_address.html"

	def get_success_url(self, *args, **kwargs):
		return reverse("user_address_list")

	def form_valid(self, form, *args, **kwargs):
		form.instance.user = self.request.user
		return super(UserAddressUpdateView, self).form_valid(form, *args, **kwargs)

def delete_address(request, pk):
	data = {}
	try:
		address = UserAddress.objects.get(id=pk)
		address.delete()
		data['status'] = 1
	except:data['status'] = 0
	return HttpResponse(json.dumps(data))


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
	model = User
	form_class = UserProfileForm
	template_name = "users/profile.html"

	def get_success_url(self):
		messages.success(self.request, "Profile Updated!")
		return reverse("user_profile", args=[self.request.user.id])

	# def form_valid(self, form, *args, **kwargs):
	# 	form.instance.user = self.request.user
	# 	return super(UserAddressUpdateView, self).form_valid(form, *args, **kwargs)


class LowStockProducts(OnlyStaffRequiredMixin, TemplateView):
    template_name = 'users/staff/low_stock_products.html'

    def get_context_data(self, **kwargs):
        context = super(LowStockProducts, self).get_context_data(**kwargs)
        key = {}
        if not self.request.user.is_admin:
        	key['product__created_by'] = self.request.user
        else:
        	if self.request.GET.get('filterby') and self.request.GET['filterby'] == 'my':
        		key['product__created_by'] = self.request.user
        		context['filterby'] = self.request.GET['filterby']

        context['variants'] = ProductVariant.objects.annotate(
						        	available=F('stocks__quantity')-F('stocks__quantity_allocated')
						        ).filter(
						        	available__lte=3, product__status='A', **key
						        ).order_by('available','id')
        return context

    def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		if request.is_ajax():
			try:
				variant_id = request.GET.get('variant_id')
				if variant_id:
					data = {}
					stock = Stock.objects.get(variant_id=variant_id)
					qty = int(request.GET.get('qty'))
					if qty >= stock.quantity_allocated:
						stock.quantity = qty
						stock.save()
					else:
						data['qty'] = stock.quantity_allocated
					data['status'] = 1
					return JsonResponse(data)
			except:pass
			return JsonResponse({'status':0})
		return self.render_to_response(context)


def access_denied(request,template='users/no-permission.html'):
    return render(request, template)









# class StaffManagementView(AdminRequiredMixin, ListView):
# 	template_name = 'users/user_management.html'
# 	paginate_by = 1

# 	def get_queryset(self):
# 		key = {'is_staff':True,'is_superuser':False}
# 		user_status = self.request.GET.get('s','A')
# 		if user_status == 'A':key['is_active'] = True
# 		else:key['is_active'] = False
# 		staffs = User.objects.filter(**key).order_by('first_name')
# 		return staffs

# 	def get_context_data(self, **kwargs):
# 	    context = super(StaffManagementView, self).get_context_data(**kwargs)
# 	    context['roles'] = Group.objects.all().order_by('name')
# 	    return context

# 	def paginate_queryset(self, queryset, page_size):
# 	    """
# 	    Paginate the queryset, if needed.
# 	    """
# 	    paginator = self.get_paginator(
# 	        queryset, page_size, orphans=self.get_paginate_orphans(),
# 	        allow_empty_first_page=self.get_allow_empty())
# 	    page_kwarg = self.page_kwarg
# 	    page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
# 	    try:
# 	        page_number = int(page)
# 	    except ValueError:
# 	        if page == 'last':
# 	            page_number = paginator.num_pages
# 	        else:
# 	            raise Http404(_("Page is not 'last', nor can it be converted to an int."))
# 	    try:
# 	        page = paginator.page(page_number)
# 	        return (paginator, page, page.object_list, page.has_other_pages())
# 	    except InvalidPage as e:
# 	    	try:
# 	    		page = paginator.page(page_number-1)
# 	    		return (paginator, page, page.object_list, page.has_other_pages())
# 	    	except:
# 		        raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
# 		            'page_number': page_number,
# 		            'message': str(e)
# 				})

# 	def get(self, request, *args, **kwargs):
# 		self.object_list = self.get_queryset()

# 		if request.is_ajax():
# 			html_data = {}
# 			staff_id = request.GET.get('staff_id')
# 			skey = request.GET.get('key')
# 			if staff_id:
# 				staff = User.objects.get(id=staff_id)
# 				if request.GET.get('status'):
# 					if request.GET.get('status','A') == 'A':staff.is_active = True
# 					else: staff.is_active = False
# 					staff.save()
# 					html_data['status'] = 1
# 				elif request.GET.get('role_id'):
# 					grp = Group.objects.get(id=int(request.GET.get('role_id')))
# 					staff.groups.clear()
# 					staff.groups.add(grp)
# 					return JsonResponse({'status':1})
# 				elif request.GET.get('delete'):
# 					staff.delete()

# 			if skey:
# 				self.object_list = self.get_queryset().filter(
# 					Q(first_name__startswith=skey)|Q(last_name__startswith=skey)|Q(email__startswith=skey)
# 				)

# 			context = self.get_context_data(**kwargs)
# 			html_data['html'] = render_to_string('users/part_staff_users.html',context,context_instance=RequestContext(request))
# 			return JsonResponse(html_data)

# 		context = self.get_context_data(**kwargs)
# 		return self.render_to_response(context)

# 	def post(self, request, *args, **kwargs):
# 		self.object_list = self.get_queryset()
		
# 		if request.is_ajax():
# 			html_data = {}

# 			context = self.get_context_data(**kwargs)
# 			html_data['html'] = render_to_string('users/part_staff_users.html',context,context_instance=RequestContext(request))
# 			return JsonResponse(html_data)

# 		messages.error(request, "Please select a category")
# 		messages.success(request, "Import Complete")
# 		context = self.get_context_data(**kwargs)
# 		return render(request, self.template_name, {})


# class StaffRoleDeleteView(AdminRequiredMixin, View):

# 	def post(self, request, *args, **kwargs):
# 		data = {}
# 		roleId = request.POST.get('role_id')
# 		try:
# 			if roleId:
# 				Group.objects.get(id=roleId).delete()
# 				return JsonResponse({'status':1})
# 		except:pass
# 		return JsonResponse({'status':0})

# class StaffInviteView(AdminRequiredMixin, View):

# 	def post(self, request, *args, **kwargs):
# 		invite_emails = request.POST.getlist('invite_email')
# 		sign_up_url = 'http://127.0.0.1:8000/signup'
# 		from_name = request.user.first_name

# 		subject = 'Staff Sign up Invite'
# 		body = 'Hi, <br><br>'
# 		body += 'You have been invited to sign up as staff by %s<br><br>' % request.user.first_name
# 		body += 'Click the link below to sign up<br>'

# 		for email in request.POST.getlist('invite_email',[]):
# 			if email:
# 				encoded = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256')
# 				staff_sign_up_url = sign_up_url+'?staff=%s' % encoded
# 				body += '<a target="_blank" href="%s">Staff Sign Up</a><br>' % staff_sign_up_url
# 				send_mg_email(subject, body, from_name=from_name, to_email=[email])

# 		return JsonResponse({'status':1})


# class StaffRoleView(AdminRequiredMixin, TemplateView):
#     template_name = 'users/permissions.html'

#     def get_context_data(self, **kwargs):
#         context = super(StaffRoleView, self).get_context_data(**kwargs)
#         context['parent_cats'] = CatalogCategory.objects.filter(parent__isnull=True).order_by('name')
#         return context

#     def get(self, request, *args, **kwargs):
# 		context = self.get_context_data(**kwargs)

# 		if request.is_ajax() and request.GET.get('delete') and request.GET.get('role_id'):
# 			data = {}
# 			try:
# 				role = Group.objects.get(id=int(request.GET.get('role_id')))
# 				role.delete()
# 				data['status'] = 1
# 			except:data['status'] = 0
# 			return JsonResponse(data)

# 		if kwargs.get('pk'):
# 			role = Group.objects.get(id=kwargs['pk'])
# 			context['role'] = role
# 			context['permissions'] = role.permissions.values_list('codename', flat=True)
		
# 		return self.render_to_response(context)

#     def post(self, request, *args, **kwargs):
#     	context = self.get_context_data(**kwargs)

#     	perms = request.POST.getlist('perms',[])
#     	pcats = request.POST.getlist('parent_category',[])
#     	grp_id = request.POST.get('grp_id',False)
#     	grp_name = request.POST.get('role_name',False)

#     	if grp_id:
#     		grp = Group.objects.get(id=grp_id)
#     		grp.name = grp_name
#     		grp.save()
#     		grp.permissions.clear()
#     		grp.details.categories.clear()
#     		messages.success(request, "Role updated successfully!")
#     	else:
#     		grp = Group.objects.create(name=grp_name)
#     		GroupDetails.objects.create(group=grp)
#     		messages.success(request, "Role added successfully!")

#     	grp.permissions = Permission.objects.filter(codename__in=perms)
#     	grp.details.categories = CatalogCategory.objects.filter(id__in=pcats)

#     	context['role'] = grp
#     	context['permissions'] = grp.permissions.values_list('codename', flat=True)

#         return render(request, self.template_name, context)














# class StaffRoleCreateView(CreateView):
# 	form_class = UserAddressForm
# 	template_name = "orders/add_address.html"

# 	def form_valid(self, form, *args, **kwargs):
# 		form.instance.user = self.request.user
# 		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

# class StaffRoleUpdateView(UpdateView):
# 	model = UserAddress
# 	form_class = UserAddressForm
# 	template_name = "orders/add_address.html"

# 	def form_valid(self, form, *args, **kwargs):
# 		form.instance.user = self.request.user
# 		return super(UserAddressUpdateView, self).form_valid(form, *args, **kwargs)




















