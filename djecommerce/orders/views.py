from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView, FormView, UpdateView
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

class ShippingAddressSelectView(LoginRequiredMixin, CartOrderMixin, TemplateView):
	template_name = "orders/shipping_address_select.html"

	def dispatch(self, *args, **kwargs):
		s_address = UserAddress.objects.filter(user=self.request.user,type='shipping').exists()
		if not s_address:
			return HttpResponseRedirect(reverse("order-address-add")+'?address_type=shipping')
		else:
			return super(ShippingAddressSelectView, self).dispatch(*args, **kwargs)

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		order = self.get_order()
		s_address = UserAddress.objects.filter(user=self.request.user,type='shipping')

		if order.shipping_address != None:
			context['default_ship_address'] = order.shipping_address
		else:
			default_saddr = s_address.filter(default=True)
			context['default_ship_address'] = default_saddr[0] if default_saddr else False
		context["shipping_address"] = s_address
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		sid = self.request.POST.get('shipping_address',False)
		if sid:
			try:
				s_address = UserAddress.objects.get(id=sid, user=self.request.user, type='shipping')
				order = self.get_order()
				order.shipping_address = s_address
				order.save()
				return HttpResponseRedirect(reverse("billing-order-address"))
			except:pass
		messages.error(request, "Please select a shipping address")
		context["shipping_address"] = UserAddress.objects.filter(user=self.request.user,type='shipping')
		return render(request, self.template_name, context)


class BillingAddressSelectView(LoginRequiredMixin, CartOrderMixin, TemplateView):
	template_name = "orders/billing_address_select.html"

	def dispatch(self, *args, **kwargs):
		order = self.get_order()
		b_address= UserAddress.objects.filter(user=self.request.user,type='billing').exists()
		if not order.shipping_address:
			return HttpResponseRedirect(reverse("shipping-order-address"))
		elif not b_address:
			return HttpResponseRedirect(reverse("order-address-add")+'?address_type=billing')
		else:
			return super(BillingAddressSelectView, self).dispatch(*args, **kwargs)

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		order = self.get_order()
		b_address = UserAddress.objects.filter(user=self.request.user,type='billing')

		if order.billing_address != None:
			context['default_bill_address'] = order.billing_address

		context["billing_address"] = b_address
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		order = self.get_order()
		shipping_address = order.shipping_address
		context = self.get_context_data(**kwargs)
		bid = self.request.POST.get('billing_address',False)
		same_as_shipping = self.request.POST.get('same_address',False)
		if bid or same_as_shipping:
			try:
				if same_as_shipping:
					b_address = shipping_address.get_similar_billing_address()
					if not b_address:
						b_address = shipping_address
						b_address.id = None
						b_address.type = 'billing'
						b_address.save()
				else:
					b_address = UserAddress.objects.get(id=bid, user=self.request.user, type='billing')
				order.billing_address = b_address
				order.save()
				return HttpResponseRedirect(reverse("checkout"))
			except:pass
		messages.error(request, "Please select a billing address")
		context["billing_address"] = UserAddress.objects.filter(user=self.request.user,type='billing')
		return render(request, self.template_name, context)


class OrderAddressCreateView(LoginRequiredMixin, CartOrderMixin, CreateView):
	form_class = UserAddressForm
	template_name = "orders/add_address.html"

	def get_success_url(self, *args, **kwargs):
		address_type = self.request.GET.get('address_type',False)
		if address_type == 'shipping':
			return reverse("shipping-order-address")
		else:
			return reverse("billing-order-address")

	def get_context_data(self, **kwargs):
	    context = super(OrderAddressCreateView, self).get_context_data(**kwargs)
	    address_type = self.request.GET.get('address_type',False)
	    if address_type:
	    	context['address_type'] = address_type
	    	context['form'].fields["type"].initial = address_type
	    return context

	def form_valid(self, form, *args, **kwargs):
		form.instance.user = self.request.user
		self.object = form.save()
		order = self.get_order()
		if form.instance.type == 'shipping':
			order.shipping_address = self.object
		else:
			order.billing_address = self.object
		order.save()

		return HttpResponseRedirect(self.get_success_url())

class OrderAddressUpdateView(LoginRequiredMixin, UpdateView):
	model = UserAddress
	form_class = UserAddressForm
	template_name = "orders/add_address.html"

	def get_success_url(self, *args, **kwargs):
		address_type = self.request.GET.get('address_type',False)
		if address_type == 'shipping':
			return reverse("shipping-order-address")
		else:
			return reverse("billing-order-address")

	def get_context_data(self, **kwargs):
	    context = super(OrderAddressUpdateView, self).get_context_data(**kwargs)
	    address_type = self.request.GET.get('address_type',False)
	    if address_type:
	    	context['address_type'] = address_type
	    return context

	def form_valid(self, form, *args, **kwargs):
		form.instance.user = self.request.user
		return super(OrderAddressUpdateView, self).form_valid(form, *args, **kwargs)