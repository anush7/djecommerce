from __future__ import unicode_literals
import os
import json
import uuid
from django.db import models
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, reverse_lazy

from users.models import EcUser as User
from catalog.models import CatalogCategory
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


class ProductCategory(models.Model):
    product = models.ForeignKey('Product')
    category = models.ForeignKey(CatalogCategory)

class Product(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.FloatField(null=True, editable=False)
    available_on = models.DateTimeField(blank=True, null=True)

    attributes = models.ManyToManyField('ProductAttribute', related_name='products', blank=True)
    categories = models.ManyToManyField(CatalogCategory, through='ProductCategory')

    status = models.CharField(max_length=1,default='A')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,related_name='created_products')
    modified_by = models.ForeignKey(User,related_name='modified_products', null=True, blank=True)
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        url = reverse('staff-product-edit', args=[self.id])
        # url = reverse('staff-product-edit', kwargs={"pk": self.id})
        return url

    def get_variants_url(self):
        return reverse('staff-variant-list', args=[self.id])

    def get_stocks_url(self):
        return reverse('staff-stock-list', args=[self.id])

    def get_images_url(self):
        return reverse('staff-image-list', args=[self.id])

    def get_cover_image(self):
        image = ''
        variant = ProductVariant.objects.get(default =True, product_id=self.id)
        images = ProductImage.objects.filter(variant_id=variant.id)
        if images:image = images[0].image.url
        return image

    def get_default_variant_images(self):
        image = []
        variant = ProductVariant.objects.get(default =True, product_id=self.id)
        images = [imgobj.image.url for imgobj in ProductImage.objects.filter(variant_id=variant.id)]
        return images



class ProductVariant(models.Model):
    sku = models.CharField(max_length=32, unique=True)
    default = models.BooleanField(default=False)
    name = models.CharField(max_length=100,blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    attributes = JSONField(default={})
    product = models.ForeignKey(Product, related_name='variants')

    def __str__(self):
        return self.name

    def get_display_label(self):
        label = self.name+', '
        try:attributes = self.attributes.iteritems()
        except:attributes = json.loads(self.attributes).iteritems()
        for attr_id,attr_value in attributes:
            attr_name = ProductAttribute.objects.get(id=attr_id).name
            label += attr_name+' - '+attr_value+', '
        label = label[:-2]
        return label

    def get_checkout_display_label(self):
        label = ''
        try:attributes = self.attributes.iteritems()
        except:attributes = json.loads(self.attributes).iteritems()
        for attr_id,attr_value in attributes:
            attr_name = ProductAttribute.objects.get(id=attr_id).name
            label += attr_name+' - '+attr_value+' | '
        label = label[:-2]
        return label

    def get_price(self):
        return self.price

    def get_variant_images(self):
        image = []
        images = [imgobj.image.url for imgobj in ProductImage.objects.filter(variant_id=self.id)]
        images = ', '.join(images)
        return images


@receiver(post_delete, sender=ProductVariant)
def variant_post_delete(sender, instance, **kwargs):
    variants = ProductVariant.objects.filter(product=instance.product)
    if variants:
        variants[0].default=True
        variants[0].save()

class ProductAttribute(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)

    status = models.CharField(max_length=1,default='A')
    created_by = models.ForeignKey(User,related_name='created_attributes')
    modified_by = models.ForeignKey(User,related_name='modified_attributes', null=True, blank=True)
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProductAttributeValue(models.Model):
    attribute = models.ForeignKey(ProductAttribute, related_name='values')
    attribute_value = models.CharField(max_length=100)


class Stock(models.Model):
    location = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    quantity_allocated = models.IntegerField(default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    variant = models.ForeignKey(ProductVariant, related_name='stocks')

    def save(self, *args, **kwargs):
        super(Stock, self).save(*args, **kwargs)
        try:
            if self.quantity > self.quantity_allocated:
                self.variant.product.status = 'A'
                self.variant.product.save()
            else:
                self.variant.product.status = 'I'
                self.variant.product.save()
            # variants = self.variant.product.variants.annotate(nstocks=Count('stocks')).filter(nstocks__gt=0)
        except:
            pass



def get_product_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s-%s.%s" % (uuid.uuid4(), instance.id, ext)
    return os.path.join('product/images', filename)

class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, related_name='images')
    image = models.ImageField(upload_to=get_product_image_path, max_length=255)
    caption = models.CharField(max_length=200, null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)