import braintree
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin

from orders.mixins import CartOrderMixin
from users.forms import UserSignUpForm
from users.models import EcUser as User
from products.models import Product, ProductVariant
from carts.models import Cart, CartItem

if settings.DEBUG:
	braintree.Configuration.configure(braintree.Environment.Sandbox,
      merchant_id=settings.BRAINTREE_MERCHANT_ID,
      public_key=settings.BRAINTREE_PUBLIC,
      private_key=settings.BRAINTREE_PRIVATE)


class CartView(SingleObjectMixin, View):
	model = Cart
	template = "carts/cart.html"

	def get_object(self, *args, **kwargs):
		self.request.session.set_expiry(0) #5 minutes
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			cart = Cart()
			cart.save()
			cart_id = cart.id
			self.request.session["cart_id"] = cart_id
		cart = Cart.objects.get(id=cart_id)
		if self.request.user.is_authenticated():
			cart.user = self.request.user
			cart.save()
		citems = CartItem.objects.filter(cart=cart)
		for citem in citems:
			if citem.item.available_quantity <= 0:
				citem.out_of_stock = True
				citem.line_item_total = 0.0
				citem.save()
		cart.update_subtotal()
		return cart

	def get(self, request, *args, **kwargs):
		cart = self.get_object()
		item_id = request.GET.get("item_id")
		delete_item = request.GET.get("delete", False)
		flash_message = ""
		data = {'max_qty':False}
		if item_id:
			item_instance = get_object_or_404(ProductVariant, id=item_id)
			qty = request.GET.get("qty", 1)
			try:
				if int(qty) < 1:
					delete_item = True
			except:
				raise Http404
			cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
			if created:
				flash_message = "Successfully added to cart"
			if delete_item:
				flash_message = "Item removed successfully."
				cart_item.delete()
			else:
				if not created:
					flash_message = "Item Quantity has been updated successfully."
				if int(qty) > cart_item.item.available_quantity:
					flash_message = "Only "+str(cart_item.item.available_quantity)+" available"
					data['max_qty'] = cart_item.item.available_quantity
				else:
					cart_item.quantity = qty
					cart_item.save()
			if item_instance.available_quantity <= 0:
				data['status'] = 'not_available'
			if not request.is_ajax():
				return HttpResponseRedirect(reverse("add-to-cart"))
		
		if request.is_ajax():
			try:total = cart_item.line_item_total
			except:total = None
			try:subtotal = cart_item.cart.subtotal
			except:subtotal = None
			try:cart_total = cart_item.cart.total
			except:cart_total = None
			try:tax_total = cart_item.cart.tax_total
			except:tax_total = None
			try:total_items = cart_item.cart.items.count()
			except:total_items = 0

			data["line_total"] = total,
			data["subtotal"] = subtotal,
			data["cart_total"] = cart_total,
			data["tax_total"] = tax_total,
			data["flash_message"] = flash_message,
			data["total_items"] = total_items,
			data["deleted"] = delete_item
			
			return JsonResponse(data) 

		context = {
			"object": self.get_object()
		}
		return render(request, self.template, context)


class CheckoutView(CartOrderMixin, FormMixin, DetailView):
	model = Cart
	form_class = UserSignUpForm
	template_name = "carts/checkout.html"
	success_url = reverse_lazy("checkout")

	def get_object(self, *args, **kwargs):
		cart = self.get_cart()
		if cart == None:
			return None
		return cart

	def get_context_data(self, *args, **kwargs):
		context = super(CheckoutView, self).get_context_data(*args, **kwargs)

		if self.request.user.is_authenticated():
			context["client_token"] = self.request.user.get_client_token()
			context["order"] = self.get_order()
		else:
			context["next_url"] = self.request.build_absolute_uri()
		return context

	def get(self, request, *args, **kwargs):
		get_data = super(CheckoutView, self).get(request, *args, **kwargs)
		cart = self.get_object()
		if cart == None or not cart.total:
			return redirect("add-to-cart")
		if self.request.user.is_authenticated():
			new_order = self.get_order()
			if new_order.billing_address == None or new_order.shipping_address == None:
			 	return redirect("order_address")
		return get_data


class CheckoutFinalView(CartOrderMixin, View):
	def post(self, request, *args, **kwargs):
		order = self.get_order()
		order_total = order.order_total
		nonce = request.POST.get("payment_method_nonce")
		if nonce:
			result = braintree.Transaction.sale({
			    "amount": order_total,
			    "payment_method_nonce": nonce,
			    "billing": {
				    "postal_code": "%s" %(order.billing_address.zipcode),
				 },
			    "options": {
			        "submit_for_settlement": True
			    }
			})
			if result.is_success:
				#result.transaction.id to order
				order.mark_completed(order_id=result.transaction.id)
				messages.success(request, "Thank you for your order.")
				del request.session["cart_id"]
				del request.session["order_id"]
			else:
				#messages.success(request, "There was a problem with your order.")
				messages.success(request, "%s" %(result.message))
				return redirect("checkout")
		return redirect("checkout")

	def get(self, request, *args, **kwargs):
		return redirect("checkout")





class CartCountView(View):
	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			cart_id = self.request.session.get("cart_id")
			if cart_id == None:
				count = 0
			else:
				cart = Cart.objects.get(id=cart_id)
				count = cart.items.count()
			request.session["cart_item_count"] = count
			return JsonResponse({"count": count})
		else:
			raise Http404






















