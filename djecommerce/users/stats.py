import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import F, Count, Sum, Case, When, Q, Value, IntegerField, FloatField
from django.http import JsonResponse
from catalog.models import CatalogCategory
from products.models import Product
from users.utils import get_product_stack_query, get_product_pie_query, get_revenue_stack_query, get_revenue_pie_query, get_dates
from collections import OrderedDict
from orders.models import Order


def revenue_stats(request):
	from users.constants import month_count
	key = {}
	data = {'stack':{},'pie':{}}
	q = OrderedDict()

	chart_type = request.GET.get('chart_type','both')
	stack_chart = True if (chart_type == 'both' or chart_type == 'stack') else False
	pie_chart = True if (chart_type == 'both' or chart_type == 'pie') else False

	stat_duration = request.GET.get('duration','this_quarter')

	start, end, days = get_dates(stat_duration)
	key['order_placed__gte'] = start
	key['order_placed__lte'] = end

	if stack_chart:
		dates, q = get_revenue_stack_query(start, days, stat_duration)
		print dates

	if pie_chart:
		pq = get_revenue_pie_query()
		q.update(pq)
	
	orders = Order.objects.values('status','order_placed','cart','order_total')\
					.filter(status='paid', **key).aggregate(**q)
	
	if stack_chart:
		labels = []
		series = [{'name':'Revenue','data':[]}]
		for dt in dates:
			if stat_duration in ['this_quarter','last_quarter','this_year','last_year']:
				labels.append(dt.split('-')[1]+'-'+dt.split('-')[0])
			elif stat_duration in ['this_week','last_week']:
				labels.append(dt.split('-')[2])
			elif stat_duration in ['this_month','last_month']:
				labels.append(dt.split('-')[-1])
			series[0]['data'].append(orders[dt])

		data['stack']['categories'] = labels
		data['stack']['series'] = series

	if pie_chart:
		categories = CatalogCategory.objects.filter(parent__isnull=True)
		series = [{'name':'Revenue', 'colorByPoint': True, 'data':[]}]
		for cat in categories:
			if not orders[str(cat.id)]:orders[str(cat.id)]=0.0
			series[0]['data'].append({'name':cat.name,'y':orders[str(cat.id)]})
		data['pie']['series'] = series

	return JsonResponse(data)

def product_stats(request):
	from users.constants import month_count
	key = {}
	data = {'stack':{},'pie':{}}
	q = OrderedDict()

	chart_type = request.GET.get('chart_type','both')
	stack_chart = True if (chart_type == 'both' or chart_type == 'stack') else False
	pie_chart = True if (chart_type == 'both' or chart_type == 'pie') else False

	stat_duration = request.GET.get('duration','this_quarter')

	start, end, days = get_dates(stat_duration)
	key['created_on__gte'] = start
	key['created_on__lte'] = end

	if stack_chart:
		dates, q = get_product_stack_query(start, days, stat_duration)

	if pie_chart:
		pq = get_product_pie_query()
		q.update(pq)
	
	products = Product.objects.values('status','created_on','categories')\
					.filter(status='A', **key).aggregate(**q)
	
	if stack_chart:
		labels = []
		series = [{'name':'Products','data':[]}]
		for dt in dates:
			if stat_duration in ['this_quarter','last_quarter','this_year','last_year']:
				labels.append(dt.split('-')[1]+'-'+dt.split('-')[0])
			elif stat_duration in ['this_week','last_week']:
				labels.append(dt.split('-')[2])
			elif stat_duration in ['this_month','last_month']:
				labels.append(dt.split('-')[-1])
			series[0]['data'].append(products[dt])

		data['stack']['categories'] = labels
		data['stack']['series'] = series

	if pie_chart:
		categories = CatalogCategory.objects.filter(parent__isnull=True)
		series = [{'name':'Products', 'colorByPoint': True, 'data':[]}]
		for cat in categories:
			if not products[str(cat.id)]:products[str(cat.id)]=0.0
			series[0]['data'].append({'name':cat.name,'y':products[str(cat.id)]})
		data['pie']['series'] = series

	return JsonResponse(data)






