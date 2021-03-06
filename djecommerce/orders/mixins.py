from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from carts.models import Cart, CartItem
from .models import Order


class CartOrderMixin(object):
	def get_order(self, *args, **kwargs):
		cart = self.get_cart()
		if cart is None:
			return None
		new_order_id = self.request.session.get("order_id")
		if new_order_id is None:
			new_order = Order.objects.create(cart=cart,user=self.request.user)
			self.request.session["order_id"] = new_order.id
		else:
			new_order = Order.objects.get(id=new_order_id)
			new_order.update_order()
		return new_order

	def get_cart(self, *args, **kwargs):
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			return None
		cart = Cart.objects.get(id=cart_id)

		citems = CartItem.objects.filter(cart=cart)
		for citem in citems:
			if citem.item.available_quantity <= 0:
				citem.delete()
		cart.update_subtotal()

		if cart.items.count() <= 0:
			return None
		return cart