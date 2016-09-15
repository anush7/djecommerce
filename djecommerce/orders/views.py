from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic.detail import DetailView
from  django.views.generic.list import ListView

from users.models import EcUser as User
from .forms import AddressForm, UserAddressForm
from .mixins import CartOrderMixin
from .models import UserAddress, Order
from catalog.mixins import StaffRequiredMixin

class OrderList(StaffRequiredMixin, ListView):
	queryset = Order.objects.all()

	def get_queryset(self):
		return super(OrderList, self).get_queryset().filter(user=self.request.user)

class OrderDetail(StaffRequiredMixin, DetailView):
	model = Order

	def dispatch(self, request, *args, **kwargs):
		obj = self.get_object()
		if obj.user == self.request.user:
			return super(OrderDetail, self).dispatch(request, *args, **kwargs)
		else:
			raise Http404

class AddressSelectFormView(StaffRequiredMixin, CartOrderMixin, FormView):
	form_class = AddressForm
	template_name = "orders/address_select.html"

	def dispatch(self, *args, **kwargs):
		b_address, s_address = self.get_addresses()
		if b_address.count() == 0:
			messages.success(self.request, "Please add a billing address before continuing")
			return redirect("user-address-add")
		elif s_address.count() == 0:
			messages.success(self.request, "Please add a shipping address before continuing")
			return redirect("user-address-add")
		else:
			return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

	def get_addresses(self, *args, **kwargs):
		b_address = UserAddress.objects.filter(user=self.request.user,type='billing')
		s_address = UserAddress.objects.filter(user=self.request.user,type='shipping')
		return b_address, s_address

	def get_form(self, *args, **kwargs):
		order = self.get_order()
		b_address, s_address = self.get_addresses()
		if order.billing_address != None:
			self.initial['billing_address'] = order.billing_address
		else:
			default_baddr = b_address.filter(user=self.request.user,type='billing',default=True)
			self.initial['billing_address'] = default_baddr
		if order.shipping_address != None:
			self.initial['shipping_address'] = order.shipping_address
		else:
			default_saddr = s_address.filter(user=self.request.user,type='shipping',default=True)
			self.initial['shipping_address'] = default_saddr
		form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
		form.fields["billing_address"].queryset = b_address
		form.fields["shipping_address"].queryset = s_address
		return form

	def form_valid(self, form, *args, **kwargs):
		billing_address = form.cleaned_data["billing_address"]
		shipping_address = form.cleaned_data["shipping_address"]
		order = self.get_order()
		order.billing_address = billing_address
		order.shipping_address = shipping_address
		order.save()
		return  super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

	def get_success_url(self, *args, **kwargs):
		return reverse("checkout")


class UserAddressCreateView(StaffRequiredMixin, CreateView):
	form_class = UserAddressForm
	template_name = "orders/add_address.html"
	success_url = reverse_lazy("order_address")

	def form_valid(self, form, *args, **kwargs):
		form.instance.user = self.request.user
		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)