import requests
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.db.models import F, Count, Sum, Case, When, Value
from django.db.models import IntegerField, FloatField
from collections import OrderedDict

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

def get_product_aggregate_query(st_dt, stat_type='month'):
	labels = []
	q = OrderedDict()
	if stat_type == 'month':
		st_dt = ed_dt = st_dt - relativedelta(months=6)
		for i in [0,1,1,1,1,1,1]:
			ed_dt = ed_dt + relativedelta(months=i)
			labels.append(ed_dt.strftime('%Y-%b-%a-%d'))
			q[ed_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
										                    created_on__month=int(ed_dt.strftime('%m')),
										                    created_on__year=int(ed_dt.strftime('%Y')),
										                    then=1
										                ),
										                default=Value('0'),
										                output_field=IntegerField()
										            )
									            )
	elif stat_type == 'week':
		st_dt = ed_dt = st_dt - relativedelta(days=6)
		for i in [0,1,1,1,1,1,1]:
			ed_dt = ed_dt + relativedelta(days=i)
			labels.append(ed_dt.strftime('%Y-%b-%a-%d'))
			q[ed_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
										                    created_on__date=ed_dt.date(),
										                    then=1
										                ),
										                default=Value('0'),
										                output_field=IntegerField()
										            )
									            )
	return (labels, q)

def get_order_aggregate_query(st_dt, stat_type='month'):
	labels = []
	q = OrderedDict()
	if stat_type == 'month':
		st_dt = ed_dt = st_dt - relativedelta(months=6)
		for i in [0,1,1,1,1,1,1]:
			ed_dt = ed_dt + relativedelta(months=i)
			labels.append(ed_dt.strftime('%Y-%b-%a-%d'))
			q[ed_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
										                    order_placed__month=int(ed_dt.strftime('%m')),
										                    order_placed__year=int(ed_dt.strftime('%Y')),
										                    then=F('order_total')
										                ),
										                default=Value('0.0'),
										                output_field=FloatField()
										            )
									            )
	elif stat_type == 'week':
		st_dt = ed_dt = st_dt - relativedelta(days=6)
		for i in [0,1,1,1,1,1,1]:
			ed_dt = ed_dt + relativedelta(days=i)
			labels.append(ed_dt.strftime('%Y-%b-%a-%d'))
			q[ed_dt.strftime('%Y-%b-%a-%d')] = Sum(
													Case(
														When(
										                    order_placed__date=ed_dt.date(),
										                    then=F('order_total')
										                ),
										                default=Value('0.0'),
										                output_field=FloatField()
										            )
									            )
	return (labels, q)
