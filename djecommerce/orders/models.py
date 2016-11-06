from __future__ import unicode_literals
import json
from decimal import Decimal
from datetime import datetime
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from users.models import EcUser as User
from carts.models import Cart, CartItem
from products.models import Stock
from users.utils import send_mg_email
import pdfkit

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
		return "%s, %s, %s, %s %s" %(self.user.first_name+" "+self.user.last_name, self.street, self.city, self.state, self.zipcode)

	def get_similar_billing_address(self):
		billing_address = UserAddress.objects.filter(user=self.user,type='billing')
		for addr in billing_address:
			found = True
			if not addr.street == self.street:found = False
			if not addr.city == self.city:found = False
			if not addr.state == self.state:found = False
			if not addr.zipcode == self.zipcode:found = False
			if found:
				found = addr
				break
		return found

ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('paid', 'Paid'),
	('delivered', 'delivered'),
	('refunded', 'Refunded'),
)

class Order(models.Model):
	status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
	cart = models.ForeignKey(Cart)
	user = models.ForeignKey(User, null=True)
	billing_address = models.ForeignKey(UserAddress, related_name='billing_address', on_delete=models.SET_NULL, null=True)
	shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', on_delete=models.SET_NULL, null=True)
	shipping_total_price = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
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
		data = {'shipping':self.shipping_address.get_address(),'billing':self.billing_address.get_address()}
		ord_detail = OrderDetails.objects.create(order=self, address=json.dumps(data), paid=True)
		citems = CartItem.objects.filter(cart=self.cart)
		for citem in citems:
			stock = Stock.objects.get(variant=citem.item)
			stock.quantity_allocated += citem.quantity
			stock.save()

	def send_invoice(self):
		order = Order.objects.get(id=self.id)
		css = 'static/css/bootstrap.min.css'
		try:
			cur_sym = Currency.objects.get(id=1).currency
		except:
			cur_sym = '$'
		file_data = render_to_string('orders/order_invoice.html', {'order': order,'currency_symbol':cur_sym})
		options = {
			'margin-top': '0.25in',
			'margin-right': '0.25in',
			'margin-bottom': '0.25in',
			'margin-left': '0.25in',
		}
		pdf = pdfkit.from_string(file_data, False,options=options,css=css)
		subject = 'Your Ecommerce Order'
		body = 'Hi '+self.user.get_full_name()+',<br><br>'
		body += 'Thank you for your order.<br>'
		body += 'Order No: '+self.order_id+'<br><br>'
		body += 'Please check the attachment for a copy of your order.<br><br>'
		to_email = [self.user.email]
		file_name = 'order_'+self.order_id+'.pdf'
		send_mg_email(subject,body,to_email,files=[("attachment",(file_name, pdf))])

	def update_order(self):
		shipping_total_price = self.shipping_total_price
		cart_total = self.cart.total
		order_total = Decimal(shipping_total_price) + Decimal(cart_total)
		self.order_total = order_total
		self.save()

def order_pre_save(sender, instance, *args, **kwargs):
	try:
		shipping = Shipping.objects.get(id=1).rate
	except:
		shipping = 0.0
	instance.shipping_total_price = shipping
	cart_total = instance.cart.total
	order_total = Decimal(instance.shipping_total_price) + Decimal(cart_total)
	instance.order_total = order_total

pre_save.connect(order_pre_save, sender=Order)

class OrderDetails(models.Model):
	order = models.OneToOneField(Order, related_name='details')
	address = models.TextField()
	paid = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	processed = models.BooleanField(default=False)
	shipped = models.BooleanField(default=False)
	delivered = models.BooleanField(default=False)
	returned = models.BooleanField(default=False)


class Shipping(models.Model):
	name = models.CharField(max_length=500,blank=True, null=True)
	rate = models.DecimalField(max_digits=10, decimal_places=2)
	is_active = models.BooleanField(default=False)

ALLOWED_CURRENCIES = (
	('$', 'USD'),
)

class Currency(models.Model):
	currency = models.CharField(max_length=120, choices=ALLOWED_CURRENCIES, default='$')







