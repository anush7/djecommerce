from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from products.models import Product, ProductAttribute, ProductCategory, ProductAttributeValue, ProductVariant
from users.models import EcUser as User
from django.db.models.signals import pre_save, post_save, post_delete

class CartItem(models.Model):
	cart = models.ForeignKey("Cart")
	item = models.ForeignKey(ProductVariant)
	quantity = models.PositiveIntegerField(default=1)
	line_item_total = models.DecimalField(max_digits=10, decimal_places=2)
	out_of_stock = models.BooleanField(default=False)

	def __unicode__(self):
		return self.item.title

	def remove(self):
		return self.item.remove_from_cart()

def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
	if not instance.out_of_stock:
		qty = instance.quantity
		if qty >= 1:
			price = instance.item.get_price()
			line_item_total = Decimal(qty) * Decimal(price)
			instance.line_item_total = line_item_total

def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
	instance.cart.update_subtotal()

pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)
post_save.connect(cart_item_post_save_receiver, sender=CartItem)
post_delete.connect(cart_item_post_save_receiver, sender=CartItem)

class Cart(models.Model):
	user = models.ForeignKey(User, null=True, blank=True)
	items = models.ManyToManyField(ProductVariant, through=CartItem)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)
	subtotal = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
	tax_total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
	total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
	
	tax_percentage  = models.DecimalField(max_digits=10, decimal_places=5, default=0.085) #Not req

	def __unicode__(self):
		return str(self.id)

	def update_subtotal(self):
		subtotal = 0
		items = self.cartitem_set.filter(out_of_stock=False)
		for item in items:
			subtotal += item.line_item_total
		self.subtotal = "%.2f" %(subtotal)
		self.save()

	@property
	def cart_items(self):
		return self.cartitem_set.filter(out_of_stock=False)

	@property
	def check_for_out_of_stock_items(self):
		return self.cartitem_set.filter(out_of_stock=True).exists()
	

def cal_tax_and_total_receiver(sender, instance, *args, **kwargs):
	subtotal = Decimal(instance.subtotal)
	tax_total = 0
	taxes = Tax.objects.all()
	for tax in taxes:
		tax_total += round(subtotal * Decimal((tax.tax_percentage/100)), 2) #8.5%
	total = round(subtotal + Decimal(tax_total), 2)
	instance.tax_total = "%.2f" %(tax_total)
	instance.total = "%.2f" %(total)

pre_save.connect(cal_tax_and_total_receiver, sender=Cart)


class Tax(models.Model):
	name = models.CharField(max_length=500)
	tax_percentage = models.DecimalField(max_digits=10, decimal_places=5)
	is_active = models.BooleanField(default=False)