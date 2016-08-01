from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from users.models import EcUser as User
from django.core.urlresolvers import reverse

class Catalog(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=150)
    description = models.TextField()
    categories = models.ManyToManyField('CatalogCategory')
    pub_date = models.DateTimeField(default=datetime.now)
    
    status = models.CharField(max_length=1,default='A') #Active = A, Inactive = I
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,related_name='created_catalogs')
    modified_by = models.ForeignKey(User,related_name='modified_catalogs', null=True, blank=True)
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CatalogCategory(models.Model):
    #catalog = models.ForeignKey('Catalog',related_name='categories')
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=1,default='A') #Active = A, Inactive = I
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,related_name='created_categories')
    modified_by = models.ForeignKey(User,related_name='modified_categories', null=True, blank=True)
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        url = reverse('category-product-list', args=[self.slug])
        # url = reverse('staff-product-edit', kwargs={"pk": self.id})
        return url

















# class ProductCategory(models.Model):
#     product = models.ForeignKey('Product')
#     category = models.ForeignKey('CatalogCategory')

# class Product(models.Model):
#     title = models.CharField(max_length=300)
#     slug = models.SlugField(max_length=150)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     rating = models.FloatField(null=True, editable=False)

#     # attributes = models.ManyToManyField('ProductAttribute',through='ProductAttributeValue')
#     categories = models.ManyToManyField('CatalogCategory', through='ProductCategory')

#     status = models.CharField(max_length=1,default='A')
#     created_on = models.DateTimeField(auto_now_add=True)
#     modified_on = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(User,related_name='created_products')
#     modified_by = models.ForeignKey(User,related_name='modified_products', null=True, blank=True)
#     is_trashed = models.BooleanField(default=False)

#     def __str__(self):
#         return self.title

# class ProductAttributeGroup(models.Model):
#     name = models.CharField(max_length=120)
#     order_by = models.IntegerField(default=1)
#     status = models.CharField(max_length=1,default='A') #Active = A, Inactive = I

#     def __str__(self):
#         return self.name

# # Attribute types
# TEXT = "text"
# INTEGER = "integer"
# BOOLEAN = "boolean"
# FLOAT = "float"
# DATE = "date"
# FILE = "file"
# IMAGE = "image"
# ATTR_CHOICES = (
#     (TEXT, _("Text")),(INTEGER, _("Integer")),(BOOLEAN, _("True / False")),(FLOAT, _("Float")),
#     (DATE, _("Date")),(FILE, _("File")),(IMAGE, _("Image")),
# )
# class ProductAttribute(models.Model):
#     name = models.CharField(max_length=120)
#     category = models.ForeignKey("CatalogCategory", related_name='cat_attributes')

#     type = models.CharField(choices=ATTR_CHOICES, default=ATTR_CHOICES[0][0],max_length=20)

#     status = models.CharField(max_length=1,default='A')
#     created_by = models.ForeignKey(User,related_name='created_attributes')
#     modified_by = models.ForeignKey(User,related_name='modified_attributes', null=True, blank=True)
#     is_trashed = models.BooleanField(default=False)

#     def __str__(self):
#         return self.name

# class ProductAttributeValue(models.Model):
#     attribute = models.ForeignKey('ProductAttribute')
#     product = models.ForeignKey('Product', related_name='attribute_values')

#     value_text = models.TextField(_('Text'), blank=True, null=True)
#     value_integer = models.IntegerField(_('Integer'), blank=True, null=True)
#     value_boolean = models.NullBooleanField(_('Boolean'), blank=True)
#     value_float = models.FloatField(_('Float'), blank=True, null=True)
#     value_date = models.DateField(_('Date'), blank=True, null=True)
#     # value_file = models.FileField(upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255,blank=True, null=True)
#     # value_image = models.ImageField(upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255,blank=True, null=True)


# # class Manufacturer(models.Model):
# #     user = models.ForeignKey(User)
# #     name = models.CharField(max_length=100)
# #     slug = models.SlugField(_('Slug'), max_length=80)
# #     active = models.BooleanField(default=True)



# # class ProductImage(models.Model):
# #     product = models.ForeignKey('Product', related_name='images')
# #     original = models.ImageField(upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255)
# #     caption = models.CharField(max_length=200, blank=True)

# #     display_order = models.PositiveIntegerField(default=0)
# #     created_on = models.DateTimeField(auto_now_add=True)
