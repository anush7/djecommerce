import csv
from celery import shared_task
from products.models import Product, ProductCategory
from catalog.models import CatalogCategory

@shared_task
def import_data(data, user, csvfile_data):

	req_fields = ['title','description','price','rating','status']
	python_csv_object = csv.DictReader(csvfile_data.read().splitlines())
	
	for i, rowData in enumerate(python_csv_object):
		new_product = Product()
		row = {}
		for k in rowData.keys():row[k.replace(' ','_').lower()] = rowData[k]
		if i == 0:
			if not all(map(lambda v: v in row.keys(), req_fields)):
				break

		for field in req_fields:
			setattr(new_product, field, row[field])

		new_product.created_by = user
		new_product.save()
		subcat_ids = data.getlist('category')
		if subcat_ids:
			for cid in subcat_ids:
				subcat = CatalogCategory.objects.get(id=cid)
				ProductCategory.objects.create(product=new_product, category=subcat)


