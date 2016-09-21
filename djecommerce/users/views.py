import re
import json
import uuid
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib import messages
from django.db.models import Q, Value
from django.shortcuts import render, render_to_response, get_list_or_404,get_object_or_404
from django.template.loader import render_to_string
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import authenticate, login
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from django.core.mail import send_mail
from django.conf import settings
from users.forms import UserSignUpForm, UserProfileForm
from users.models import EcUser as User
from orders.models import UserAddress
from orders.forms import AddressForm, UserAddressForm
from catalog.mixins import AdminRequiredMixin

def home(request,template='account/home.html'):
    return render(request, template)

def landing(request,template='account/landing.html'):
    return render(request, template)

def account_settings(request,template='account/settings.html'):
    return render(request, template)

def user_signup(request, template='account/signup.html'):
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
			user=authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
			login(request, user)
			try:next_url = request.GET['next']
			except:
				try:next_url = request.POST['next']
				except:next_url = reverse('product-list')
			return HttpResponseRedirect(next_url)
	else:
		form = UserSignUpForm()
	return render(request, template, {'form': form})

def user_signin(request, template='account/signin.html'):
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

def forgot_password(request, template="account/forgot-password.html"):
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
				email_data['user'] = user
				email_data['reset_link'] = 'http://localhost:8000/accounts/reset-password/?uuid='+user.uuid
				html_content = body = render_to_string('account/reset-email.html',email_data,context_instance=RequestContext(request))
				send_mail('Password Reset Link - ContactMgmt App', body, from_email, to_email,fail_silently=False, html_message=html_content,)
				data['msg'] = 'Please check your email for password rest link'
			except:
				import sys
				print sys.exc_info()
				data['msg'] = 'Sorry, we don\'t recognize this email address'
		else:
			data['msg'] = 'Please enter your registered email address'
	return render(request, template, {'data': data})

def reset_password(request, template="account/reset-password.html"):
	data={}
	if request.POST:
		if request.POST.get('pass1',False) and request.POST.get('pass2',False):
			try:
				uuid = request.POST.get('uuid',False)
				user = User.objects.get(uuid=uuid)
				user.set_password(request.POST.get('pass1'))
				user.user.save()
				data['msg'] = 'Password reset successful'
			except:
				data['msg'] = 'Oops no able to process your request!'
		else:
			data['msg'] = 'Please enter both the fields'
		return HttpResponse(json.dumps(data))
	else:
		uuid = request.GET.get('uuid',False)
		if uuid:
			try:
				user = User.objects.get(uuid=uuid)
				data['uuid'] = uuid
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


class UserAddressListView(ListView):
    template_name = 'users/addresses.html'

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

class UserAddressCreateView(CreateView):
	form_class = UserAddressForm
	template_name = "orders/add_address.html"
	success_url = reverse_lazy("order_address")

	def form_valid(self, form, *args, **kwargs):
		form.instance.user = self.request.user
		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

class UserAddressUpdateView(UpdateView):
	model = UserAddress
	form_class = UserAddressForm
	template_name = "orders/add_address.html"
	success_url = reverse_lazy("order_address")

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


class UserProfileUpdateView(UpdateView):
	model = User
	form_class = UserProfileForm
	template_name = "account/profile.html"

	def get_success_url(self):
		messages.success(self.request, "Profile Updated!")
		return reverse("user_profile", args=[self.request.user.id])

	# def form_valid(self, form, *args, **kwargs):
	# 	form.instance.user = self.request.user
	# 	return super(UserAddressUpdateView, self).form_valid(form, *args, **kwargs)


class StaffManagementView(AdminRequiredMixin, ListView):
	template_name = 'users/user_management.html'
	paginate_by = 1

	def get_queryset(self):
		key = {'is_staff':True,'is_superuser':False}
		user_status = self.request.GET.get('s','A')
		if user_status == 'A':key['is_active'] = True
		else:key['is_active'] = False
		staffs = User.objects.filter(**key).order_by('first_name')
		return staffs

	def get_context_data(self, **kwargs):
	    context = super(StaffManagementView, self).get_context_data(**kwargs)
	    return context

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
				elif request.GET.get('delete'):
					staff.delete()

			if skey:
				self.object_list = self.get_queryset().filter(
					Q(first_name__startswith=skey)|Q(last_name__startswith=skey)|Q(email__startswith=skey)
				)

			context = self.get_context_data(**kwargs)
			html_data['html'] = render_to_string('users/part_staff_users.html',context,context_instance=RequestContext(request))
			return JsonResponse(html_data)

		context = self.get_context_data(**kwargs)
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		self.object_list = self.get_queryset()
		
		if request.is_ajax():
			html_data = {}

			context = self.get_context_data(**kwargs)
			html_data['html'] = render_to_string('users/part_staff_users.html',context,context_instance=RequestContext(request))
			return JsonResponse(html_data)

		messages.error(request, "Please select a category")
		messages.success(request, "Import Complete")
		context = self.get_context_data(**kwargs)
		return render(request, self.template_name, {})


class StaffInviteView(AdminRequiredMixin, View):

	def post(self, request, *args, **kwargs):
		invite_emails = request.POST.getlist('invite_email')
		print "11111111111111111111111111111111111111111111"
		print request.POST.getlist('invite_email')
		print "11111111111111111111111111111111111111111111"
		return JsonResponse({'status':1})


class StaffPermissionView(AdminRequiredMixin, TemplateView):
    template_name = 'users/permissions.html'

    def get_context_data(self, **kwargs):
        context = super(StaffPermissionView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.getlist('category'):
            messages.error(request, "Please select a category")
            return render(request, self.template_name, {})

        messages.success(request, "Import Complete")
        return render(request, self.template_name, {})























