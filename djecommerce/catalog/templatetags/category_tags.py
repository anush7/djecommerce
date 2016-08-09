import json
from django import template
from catalog.models import CatalogCategory
register = template.Library()


@register.assignment_tag
def get_categories():
	categories = CatalogCategory.objects.filter(parent__isnull=True).order_by('name')
	return categories