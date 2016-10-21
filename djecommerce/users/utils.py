import pytz
import requests
import datetime
import calendar
from django.conf import settings
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import timedelta
from django.db.models import F, Count, Sum, Case, When, Value
from django.db.models import IntegerField, FloatField
from collections import OrderedDict
from catalog.models import CatalogCategory

def send_mg_email(subject, body, from_name=False, to_email=[]):
	mg_url = "https://api.mailgun.net/v3/%s/messages" % (settings.MG_DOMAIN)
	mg_key = settings.MG_API_KEY
	if from_name:
		from_email = "%s <notifications@%s>" % (from_name, settings.MG_DOMAIN)

	#', '.join("{!s} <{!s}>".format(key,val) for (key,val) in to_email.items())
	msg_data = {
		"from": from_email,
		"to": ', '.join(to_email),
		"subject": subject,
		"html": body
	}
	requests.post(mg_url, auth=("api", mg_key), data=msg_data)

def get_product_stack_query(st_dt, days, duration_type='this_quarter'):
	from users.constants import month_count
	labels = []
	q = OrderedDict()
	if duration_type in ['this_quarter','last_quarter','this_year','last_year']:
		mcount = month_count[duration_type]
		for i in [1]*mcount:
			labels.append(st_dt.strftime('%Y-%b-%a-%d'))
			q[st_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
										                    created_on__month=int(st_dt.strftime('%m')),
										                    created_on__year=int(st_dt.strftime('%Y')),
										                    then=1
										                ),
										                default=Value('0'),
										                output_field=IntegerField()
										            )
									            )
			st_dt = st_dt + relativedelta(months=i)
	elif duration_type in ['this_week','last_week','this_month','last_month']:
		if duration_type in ['this_month','last_month']:mcount = days
		else:mcount = month_count[duration_type]
		for i in [1]*mcount:
			labels.append(st_dt.strftime('%Y-%b-%a-%d'))
			q[st_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
										                    created_on__date=st_dt.date(),
										                    then=1
										                ),
										                default=Value('0'),
										                output_field=IntegerField()
										            )
									            )
			st_dt = st_dt + relativedelta(days=i)
	return (labels, q)

def get_product_pie_query():
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
	return q


def get_revenue_stack_query(st_dt, days, duration_type='this_quarter'):
	from users.constants import month_count
	labels = []
	q = OrderedDict()
	if duration_type in ['this_quarter','last_quarter','this_year','last_year']:
		mcount = month_count[duration_type]
		for i in [1]*mcount:
			labels.append(st_dt.strftime('%Y-%b-%a-%d'))
			q[st_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
										                    order_placed__month=int(st_dt.strftime('%m')),
										                    order_placed__year=int(st_dt.strftime('%Y')),
										                    then=F('order_total')
										                ),
										                default=Value('0.0'),
										                output_field=FloatField()
										            )
									            )
			st_dt = st_dt + relativedelta(months=i)

	elif duration_type in ['this_week','last_week','this_month','last_month']:
		if duration_type in ['this_month','last_month']:mcount = days
		else:mcount = month_count[duration_type]
		for i in [1]*mcount:
			labels.append(st_dt.strftime('%Y-%b-%a-%d'))
			q[st_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
															order_placed__date=st_dt.date(),
										                    then=F('order_total')
										                ),
										                default=Value('0.0'),
										                output_field=FloatField()
										            )
									            )
			st_dt = st_dt + relativedelta(days=i)
	return (labels, q)

def get_revenue_pie_query():
	categories = CatalogCategory.objects.filter(parent__isnull=True)
	q = OrderedDict()
	for cat in categories:
		q[str(cat.id)] = Sum(
							Case(
								When(
				                    cart__items__product__categories__parent__in=[cat],
				                    then=F('order_total')
				                ),
				                default=Value('0.0'),
				                output_field=FloatField()
				            )
				        )
	return q


def get_dates(duration):
    qn = {1:1,2:1,3:1,4:2,5:2,6:2,7:3,8:3,9:3,10:4,11:4,12:4} 
    qd = {1:[1,3],2:[4,6],3:[7,9],4:[10,12]}
    
    dt = parse(str(datetime.datetime.now().date())+' 00:00 AM')
    if duration == 'last_week':
        start_date = (dt - timedelta(days=dt.weekday())) - timedelta(days=7)
        end_date = parse(str((start_date + timedelta(days=6)).date()) + ' 11:59:59 PM')
    elif duration == 'this_month':
        start_date = dt.replace(day = 1)
        end_date = start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
        end_date = parse(str(end_date.date()) + ' 11:59:59 PM')
    elif duration == 'last_month':
        start_date = (dt - relativedelta(months=1)).replace(day = 1)
        end_date = start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
        end_date = parse(str(end_date.date()) + ' 11:59:59 PM')
    elif duration == 'this_quarter':
        s_m, e_m = qd[qn[dt.month]]
        start_date = dt.replace(day = 1, month = s_m)
        end_date = start_date+relativedelta(months=2)
        end_date = end_date.replace(day = calendar.monthrange(end_date.year, end_date.month)[1])
        end_date = parse(str(end_date.date()) + ' 11:59:59 PM')
    elif duration == 'last_quarter':
        quater = qn[dt.month] - 1
        if quater < 1:quater = 4
        s_m, e_m = qd[quater]
        if dt.month <= 3:year = dt.year - 1
        else:year = dt.year
        start_date = dt.replace(day = 1, month = s_m, year = year)
        end_date = start_date+relativedelta(months=2)
        end_date = end_date.replace(day = calendar.monthrange(end_date.year, end_date.month)[1])
        end_date = parse(str(end_date.date()) + ' 11:59:59 PM')
    elif duration == 'this_year':
        start_date = dt.replace(day = 1, month = 1)
        end_date = dt.replace(day = 1, month = 12)
        end_date = end_date.replace(day = calendar.monthrange(end_date.year, end_date.month)[1])
        end_date = parse(str(end_date.date()) + ' 11:59:59 PM')
    elif duration == 'last_year':
        start_date = dt.replace(day = 1, month = 1, year = dt.year-1)
        end_date = start_date.replace(day = 1, month = 12)
        end_date = end_date.replace(day = calendar.monthrange(end_date.year, end_date.month)[1])
        end_date = parse(str(end_date.date()) + ' 11:59:59 PM')
    else: #duration == 'this_week'
        start_date = dt - timedelta(days=dt.weekday())
        end_date = parse(str((start_date + timedelta(days=6)).date()) + ' 11:59:59 PM')
    return [start_date.replace(tzinfo=pytz.utc), end_date.replace(tzinfo=pytz.utc), (end_date-start_date).days+1]


