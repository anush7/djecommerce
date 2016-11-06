from orders.models import Currency

def get_currency_symbol(request):
	try:
		curObj = Currency.objects.get(id=1)
		return {'currency_symbol': curObj.currency}
	except:
		return {'currency_symbol': '$'}