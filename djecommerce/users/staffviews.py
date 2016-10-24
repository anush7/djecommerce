import jwt
import json
from django.http import JsonResponse, Http404
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.paginator import InvalidPage, Paginator
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.base import View, TemplateView
from django.views.generic.list import ListView
from orders.models import Order, OrderDetails


class ProcessOrderView(ListView):
	template_name = 'users/staff/process_orders.html'
	paginate_by = 20

	def get_queryset(self):
		orders = Order.objects.filter(status='paid').order_by('order_placed')
		return orders

	def get_context_data(self, **kwargs):
	    context = super(ProcessOrderView, self).get_context_data(**kwargs)
	    #context['roles'] = Group.objects.all().order_by('name')
	    return context

	def get(self, request, *args, **kwargs):
		self.object_list = self.get_queryset()

		if request.is_ajax():
			html_data = {}
			order_id = request.GET.get('order_id')
			if order_id:
				try:
					action = request.GET.get('action')
					name = request.GET.get('name')
					orderdetail = OrderDetails.objects.get(order_id=int(order_id))
					if action == 'true':
						setattr(orderdetail,name,True)
						if name == 'delivered':
							orderdetail.order.status = 'delivered'
							orderdetail.order.save()
					else:
						setattr(orderdetail,name,False)
						if name == 'delivered':
							orderdetail.order.status = 'paid'
							orderdetail.order.save()
					orderdetail.save()
					return JsonResponse({'status':1})
				except:
					return JsonResponse({'status':0})
			else:
				context = self.get_context_data(**kwargs)
				html_data['html'] = render_to_string('users/admin/part_staff_users.html',context,context_instance=RequestContext(request))
				return JsonResponse(html_data)

		context = self.get_context_data(**kwargs)
		return self.render_to_response(context)




































