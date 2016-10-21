from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib import messages

from users.models import EcUser as User
from .forms import UserAddressForm
from .mixins import CartOrderMixin
from .models import UserAddress, Order
from users.mixins import StaffRequiredMixin, LoginRequiredMixin

class OrderList(LoginRequiredMixin, ListView):
	queryset = Order.objects.all()

	def get_queryset(self):
		return super(OrderList, self).get_queryset().filter(user=self.request.user)

class OrderDetail(LoginRequiredMixin, DetailView):
	model = Order

	def dispatch(self, request, *args, **kwargs):
		obj = self.get_object()
		if obj.user == self.request.user:
			return super(OrderDetail, self).dispatch(request, *args, **kwargs)
		else:
			raise Http404

class AddressSelectFormView(LoginRequiredMixin, CartOrderMixin, TemplateView):
	template_name = "orders/address_select.html"

	def dispatch(self, *args, **kwargs):
		b_address, s_address = self.get_addresses()
		if b_address.count() == 0:
			messages.success(self.request, "Please add a billing address before continuing")
			return HttpResponseRedirect(reverse("user-address-add")+'?checkout=True')
		elif s_address.count() == 0:
			messages.success(self.request, "Please add a shipping address before continuing")
			return HttpResponseRedirect(reverse("user-address-add")+'?checkout=True')
		else:
			return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

	def get_addresses(self, *args, **kwargs):
		b_address = UserAddress.objects.filter(user=self.request.user,type='billing')
		s_address = UserAddress.objects.filter(user=self.request.user,type='shipping')
		return b_address, s_address

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		order = self.get_order()
		b_address, s_address = self.get_addresses()

		if order.billing_address != None:
			context['default_bill_address'] = order.billing_address
		else:
			default_baddr = b_address.filter(user=self.request.user,type='billing',default=True)
			context['default_bill_address'] = default_baddr[0] if default_baddr else False
		if order.shipping_address != None:
			context['default_ship_address'] = order.shipping_address
		else:
			default_saddr = s_address.filter(user=self.request.user,type='shipping',default=True)
			context['default_ship_address'] = default_saddr[0] if default_saddr else False

		context["billing_address"] = b_address
		context["shipping_address"] = s_address
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		bid = self.request.POST.get('billing_address',False)
		sid = self.request.POST.get('shipping_address',False)
		if bid and sid:
			try:
				b_address = UserAddress.objects.get(id=bid, user=self.request.user, type='billing')
				s_address = UserAddress.objects.get(id=sid, user=self.request.user, type='shipping')
				order = self.get_order()
				order.billing_address = b_address
				order.shipping_address = s_address
				order.save()
				return HttpResponseRedirect(reverse("checkout"))
			except:pass
		messages.error(request, "Please select billing and shipping address")
		b_address, s_address = self.get_addresses()
		context["billing_address"] = b_address
		context["shipping_address"] = s_address
		return render(request, self.template_name, context)