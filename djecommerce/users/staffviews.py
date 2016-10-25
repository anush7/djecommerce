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
from users.mixins import StaffRequiredMixin


class ProcessOrderView(StaffRequiredMixin, ListView):
	template_name = 'users/staff/process_orders.html'
	paginate_by = 1
	permissions = ['process_orders']

	def get_queryset(self):
		key = {}
		filterby  = self.request.GET.get('filter',False)
		if filterby in ['paid','approved', 'processed', 'shipped', 'delivered', 'returned']:
			key['details__'+filterby] = True
		elif filterby in ['-approved', '-processed', '-shipped', '-delivered', '-returned']:
			key['details__'+filterby[1:]] = False
		orders = Order.objects.filter(**key).order_by('order_placed')
		return orders

	def paginate_queryset(self, queryset, page_size):
	    """
	    Paginate the queryset, if needed.
	    """
	    paginator = self.get_paginator(
	        queryset, page_size, orphans=self.get_paginate_orphans(),
	        allow_empty_first_page=self.get_allow_empty())
	    page_kwarg = self.page_kwarg
	    page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
	    try:
	        page_number = int(page)
	    except ValueError:
	        if page == 'last':
	            page_number = paginator.num_pages
	        else:
	            raise Http404(_("Page is not 'last', nor can it be converted to an int."))
	    try:
	        page = paginator.page(page_number)
	        return (paginator, page, page.object_list, page.has_other_pages())
	    except InvalidPage as e:
	    	try:
	    		page = paginator.page(page_number-1)
	    		return (paginator, page, page.object_list, page.has_other_pages())
	    	except:
		        raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
		            'page_number': page_number,
		            'message': str(e)
				})

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
				html_data['html'] = render_to_string('users/staff/part_process_orders.html',context,context_instance=RequestContext(request))
				html_data['paginatehtml'] = render_to_string('users/staff/part_pagination.html',context,context_instance=RequestContext(request))
				return JsonResponse(html_data)

		context = self.get_context_data(**kwargs)
		return self.render_to_response(context)




































