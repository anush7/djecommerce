from __future__ import unicode_literals
from decimal import Decimal
from datetime import datetime
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.core.urlresolvers import reverse

from users.models import EcUser as User
from carts.models import Cart

ADDRESS_TYPE = (
	('billing', 'Billing'),
	('shipping', 'Shipping'),
)

class UserAddress(models.Model):
	user = models.ForeignKey(User)
	type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
	street = models.CharField(max_length=120)
	city = models.CharField(max_length=120)
	state = models.CharField(max_length=120)
	zipcode = models.CharField(max_length=120)
	default = models.BooleanField(default=False)

	def __unicode__(self):
		return self.street+", "+self.city+", "+self.state+", "+self.zipcode+"."

	def get_address(self):
		return "%s, %s, %s %s" %(self.street, self.city, self.state, self.zipcode)


ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('paid', 'Paid'),
	('shipped', 'Shipped'),
	('refunded', 'Refunded'),
)

class Order(models.Model):
	status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
	cart = models.ForeignKey(Cart)
	user = models.ForeignKey(User, null=True)
	billing_address = models.ForeignKey(UserAddress, related_name='billing_address', null=True)
	shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', null=True)
	shipping_total_price = models.DecimalField(max_digits=50, decimal_places=2, default=5.99)
	order_total = models.DecimalField(max_digits=50, decimal_places=2, )
	order_id = models.CharField(max_length=20, null=True, blank=True)
	order_placed = models.DateTimeField(blank=True, null=True)

	def __unicode__(self):
		return str(self.cart.id)

	class Meta:
		ordering = ['-id']

	def get_absolute_url(self):
		return reverse("order_detail", kwargs={"pk": self.pk})

	def mark_completed(self, order_id=None):
		self.status = "paid"
		if order_id and not self.order_id:
			self.order_id = order_id
		self.order_placed = datetime.now()
		self.save()

	def update_order(self):
		shipping_total_price = self.shipping_total_price
		cart_total = self.cart.total
		order_total = Decimal(shipping_total_price) + Decimal(cart_total)
		self.order_total = order_total
		self.save()


def order_pre_save(sender, instance, *args, **kwargs):
	shipping_total_price = instance.shipping_total_price
	cart_total = instance.cart.total
	order_total = Decimal(shipping_total_price) + Decimal(cart_total)
	instance.order_total = order_total

pre_save.connect(order_pre_save, sender=Order)













