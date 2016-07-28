import json
from django import template
register = template.Library()
from products.models import ProductAttribute


@register.filter(name='attr_json_filter')
def attribute_json_filter(value, arg):
	val = '--'
	try:val = value[str(arg)]
	except:
		try:val = json.loads(value)[str(arg)]
		except:pass
	return val

@register.filter(name='get_attr_val')
def get_attr_val(varient, attr_id):
	val = ''
	try:
		val = varient.attributes[str(attr_id)]
	except:
		try:val = json.loads(varient.attributes)[str(attr_id)]
		except:pass
	return val

@register.filter(name='get_variant_images')
def get_variant_images(varient):
	images = []
	try:images = varient.images.all()
	except:pass
	return images
