import json
from django.http import HttpResponse, HttpResponseRedirect  
from django.shortcuts import render, render_to_response, get_list_or_404,get_object_or_404
from django.template.loader import render_to_string
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.defaultfilters import slugify

from django.views.generic.list import ListView
from django.views.generic import View
from django.views.generic.edit import *
from django.views.generic.detail import (
    BaseDetailView, SingleObjectMixin, SingleObjectTemplateResponseMixin,DetailView,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger

from users.models import EcUser as User
from catalog.models import Catalog, CatalogCategory
from products.models import Product, ProductAttribute, ProductCategory, ProductAttributeValue, ProductVariant, Stock, ProductImage
from products.forms import ProductForm, VariantForm, StockForm, ProductImageForm
from products.utils import image_cropper, get_unique_slug, decimal_default


class ProductListView(ListView):
    paginate_by = 8
    context_object_name = 'product'
    template_name = 'products/frontend/products.html'

    def get_queryset(self):
        # del self.request.session["cart_id"]
        # del self.request.session["order_id"]
        key = {}
        html_data = {}
        key['status'] = 'A'
        slug = self.kwargs.get('slug',False)
        q = self.request.GET.get('q', False)
        if slug:key['categories__slug'] = slug
        if q:
            q_text = (Q(title__icontains=q)|Q(description__icontains=q))
            products = Product.objects.filter(q_text, **key).order_by('created_on')
        else:
            products = Product.objects.filter(**key).order_by('created_on')
        return products

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        slug = self.kwargs.get('slug',False)
        q = self.request.GET.get('q', False)
        if slug:context['subCat'] = CatalogCategory.objects.get(slug=slug)
        if q:context['search_key'] = q
        return context

def ajax_product_list(request, template='products/frontend/part_product_list.html'):
    data = {}
    html_data = {}
    key = {}
    q = request.GET.get('q', False)
    category_id = request.GET.get('c', False)
    key['status'] = 'A'

    if category_id:
        try:
            html_data['pcat_name'] = CatalogCategory.objects.get(id=category_id).parent.name
            html_data['scat_name'] = CatalogCategory.objects.get(id=category_id).name
            key['categories__id__in'] = [category_id]
        except:pass

    if q:
        html_data['search_key'] = q
        q_text = (Q(title__icontains=q)|Q(description__icontains=q))
        product_list = Product.objects.filter(q_text, **key).order_by('created_on')
    else:
        product_list = Product.objects.filter(**key).order_by('created_on')

    try:page = request.GET.get('page')
    except:page = 1
    paginator = Paginator(product_list, 8)
    try:
        product_list = paginator.page(page)
    except PageNotAnInteger:
        product_list = paginator.page(1)
    except EmptyPage:
        product_list = paginator.page(paginator.num_pages)

    try:next_page = product_list.next_page_number
    except:next_page = False

    page_obj = {
        'has_previous': product_list.has_previous,
        'previous_page_number' : product_list.previous_page_number,
        'number' : product_list.number,
        'paginator' : product_list.paginator,
        'has_next' : product_list.has_next,
        'next_page_number' : product_list.next_page_number
    }

    data['object_list'] = product_list
    data['page_obj'] = page_obj
    html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
    html_data['page'] = 1
    return HttpResponse(json.dumps(html_data))


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/frontend/product_detail.html'

    def get_queryset(self):
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        try:context['default_variant'] = ProductVariant.objects.get(default=True, product_id=self.kwargs['pk'])
        except:messages.success(self.request, "Product inactive. No variants available!")
        product = self.get_object()
        context['related_products'] = Product.objects.filter(status='A',categories__in=product.categories.all()).exclude(id=product.id).distinct()[:4]
        return context


class VariantImageView(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            var_id = self.request.GET.get('var_id')
            varient = ProductVariant.objects.get(id=var_id)
            if cart_id == None:
                count = 0
            else:
                cart = Cart.objects.get(id=cart_id)
                count = cart.items.count()
            request.session["cart_item_count"] = count
            return JsonResponse({"count": count})
        else:
            raise Http404




#not req
def GetVariantPrice(request):
    data = {}
    variant_id = request.GET['variant_id']
    try:
        vprice = ProductVariant.objects.get(id=variant_id).price
        data['price'] = vprice
        data['status'] = 1
    except:
        import sys
        print sys.exc_info()
        data['status'] = 0
    return HttpResponse(json.dumps(data, default=decimal_default))