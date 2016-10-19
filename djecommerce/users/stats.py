import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import F, Count, Sum, Case, When, Q, Value, IntegerField
from django.http import JsonResponse
from catalog.models import CatalogCategory
from products.models import Product
from users.utils import get_product_aggregate_query, get_order_aggregate_query
from collections import OrderedDict
from orders.models import Order

def orders_added_stats(request):
	data={}
	stat_duration = request.GET.get('duration','month')

	now = datetime.now()
	dates, q = get_order_aggregate_query(now, stat_duration)

	if stat_duration == 'month':
		start_dt = now - relativedelta(months=6)
	elif stat_duration == 'week':
		start_dt = now - relativedelta(days=6)

	orders = Order.objects.values('status', 'order_placed')\
					.filter(status='A', order_placed__date__gte=start_dt.date()).aggregate(**q)

	print "oooooooooooooooooooooooooooooooooooo"
	print orders
	print dates
	print q
	print "oooooooooooooooooooooooooooooooooooo"

	labels = []
	series = [{'name':'Orders','data':[]}]
	for dt in dates:
		if stat_duration == 'week':
			labels.append(dt.split('-')[2])
		elif stat_duration == 'month':
			labels.append(dt.split('-')[1])
		series[0]['data'].append(orders[dt])

	data['categories'] = labels
	data['series'] = series
	return JsonResponse(data)

def products_added_stats(request):
	data={}
	stat_duration = request.GET.get('duration','month')

	now = datetime.now()
	dates, q = get_product_aggregate_query(now, stat_duration)

	if stat_duration == 'month':
		start_dt = now - relativedelta(months=6)
	elif stat_duration == 'week':
		start_dt = now - relativedelta(days=6)

	products = Product.objects.values('status', 'created_on')\
					.filter(status='A', created_on__date__gte=start_dt.date()).aggregate(**q)

	labels = []
	series = [{'name':'Products','data':[]}]
	for dt in dates:
		if stat_duration == 'week':
			labels.append(dt.split('-')[2])
		elif stat_duration == 'month':
			labels.append(dt.split('-')[1])
		series[0]['data'].append(products[dt])

	data['categories'] = labels
	data['series'] = series
	return JsonResponse(data)


def products_by_cats(request):
	data = {}

	categories = CatalogCategory.objects.filter(parent__isnull=True)
	q = OrderedDict()
	for cat in categories:
		q[str(cat.id)] = Sum(
						Case(
							When(
			                    categories__parent__in=[cat],
			                    then=1
			                ),
			                default=Value('0'),
			                output_field=IntegerField()
			            )
			        )

	products = Product.objects.values('status','categories').filter(status='A').aggregate(**q)
	
	series = [{'name':'Products', 'colorByPoint': True, 'data':[]}]
	for cat in categories:
		series[0]['data'].append({'name':cat.name,'y':products[str(cat.id)]})

	data['series'] = series
	return JsonResponse(data)











