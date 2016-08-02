import json
from django.http import HttpResponse, HttpResponseRedirect  
from django.shortcuts import render, render_to_response, get_list_or_404,get_object_or_404
from django.template.loader import render_to_string
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
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
from products.utils import image_cropper, get_unique_slug


class ProductListView(ListView):
    paginate_by = 8
    template_name = 'products/product_list.html'

    def get_queryset(self):
        return Product.objects.filter(status='A').order_by('created_on')

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['categories'] = CatalogCategory.objects.filter(parent__isnull=True).order_by('name')
        return context

@csrf_exempt
def ajax_product_list(request, template='products/part_product_list.html'):
    data = {}
    html_data = {}
    key = {}
    q_text=False

    q = request.GET.get('q', False)
    category_id = request.GET.get('c', False)
    status = request.GET.get('s', 'A')

    if status:key['status'] = status
    if category_id:
        try:
            html_data['cat_name'] = CatalogCategory.objects.get(id=category_id).name
            key['categories__id__in'] = [category_id]
        except:pass

    if q:q_text = (Q(title__icontains=q)|Q(description__icontains=q))

    if q_text:
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

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-variant-list',args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        context['parent_cats'] = pcat = CatalogCategory.objects.annotate(nsubcats=Count('children')).filter(
                                        parent__isnull=True,
                                        nsubcats__gt=0
                                ).order_by('name')
        if pcat:
            context['sub_cats'] = CatalogCategory.objects.filter(
                                    parent=pcat[0],
                                ).order_by('name')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.status = self.request.POST.get('submit','I')
        self.object.save()
        form.save_m2m()
        subcat_ids = self.request.POST.getlist('category')
        if subcat_ids:
            ProductCategory.objects.filter(product=self.object).delete()
            for cid in subcat_ids:
                subcat = CatalogCategory.objects.get(id=cid)
                ProductCategory.objects.create(product=self.object, category=subcat)
        attribute_ids = self.request.POST.getlist('attributes')

        return HttpResponseRedirect(self.get_success_url())

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-variant-list',args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateView, self).get_context_data(**kwargs)
        context['product'] = product = self.get_object()
        context['parent_cats'] = CatalogCategory.objects.annotate(nsubcats=Count('children')).filter(
                                    parent__isnull=True,
                                    nsubcats__gt=0
                                ).order_by('name')
        subcat = product.categories.all()
        context['selected_parent_cat'] = subcat[0].parent
        context['sub_cats'] = CatalogCategory.objects.filter(parent=subcat[0].parent).order_by('name')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.modified_by = self.request.user
        self.object.save()
        form.save_m2m()
        subcat_ids = self.request.POST.getlist('category')
        if subcat_ids:
            ProductCategory.objects.filter(product=self.object).delete()
            for cid in subcat_ids:
                subcat = CatalogCategory.objects.get(id=cid)
                ProductCategory.objects.create(product=self.object, category=subcat)
        return HttpResponseRedirect(self.get_success_url())

def delete_product(request, pk):
    data = {}
    try:
        product = Product.objects.get(id=pk)
        product.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))


class ProductDetailView(DetailView):
    model = Product

    def get_queryset(self):
        return Product.objects.all()

def get_sub_cats(request, template="products/load_sub_cats.html"):
    data = {}
    html_data = {}
    pk = request.POST.get('pid')
    product_id = request.POST.get('product_id')
    if product_id:
        product = Product.objects.get(id=product_id)
        data['product'] = product
    try:
        parent_cat = CatalogCategory.objects.get(id=pk)
        data['sub_cats'] = parent_cat.children.all()
        html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
        html_data['status'] = 1
    except:
        html_data['status'] = 0
    return HttpResponse(json.dumps(html_data))

"""########################### VARIANTS VIEWS ############################"""

class VariantListView(ListView):
    template_name = 'products/variant_list.html'

    def get_queryset(self):
        return ProductVariant.objects.filter(product_id=self.kwargs['pid']).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(VariantListView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        return context

class VariantCreateView(CreateView):
    model = ProductVariant
    form_class = VariantForm
    template_name = 'products/variant_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-variant-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        context = super(VariantCreateView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.product = product = Product.objects.get(id=self.kwargs['pid'])
        data = {} 
        for attr in product.attributes.all():
            data[attr.id] = self.request.POST.get(str(attr.id))
        self.object.attributes = data
        if form.cleaned_data['default']:
            ProductVariant.objects.filter(product_id=self.kwargs['pid'], default=True).update(default=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class VariantUpdateView(UpdateView):
    model = ProductVariant
    form_class = VariantForm
    template_name = 'products/variant_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-variant-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        context = super(VariantUpdateView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.product = product = Product.objects.get(id=self.kwargs['pid'])
        data = {}
        for attr in product.attributes.all():
            print self.request.POST.get(str(attr.id))
            data[attr.id] = self.request.POST.get(str(attr.id))
        self.object.attributes = data
        if form.cleaned_data['default']:
            ProductVariant.objects.filter(product_id=self.kwargs['pid'], default=True).update(default=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

def VariantDeleteView(request, pid):
    data = {}
    try:
        variant_ids = request.POST.get('variant_ids').split(',')
        variants = ProductVariant.objects.filter(id__in=variant_ids)
        variants.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))

"""########################### STOCKS VIEWS ############################"""

class StockListView(ListView):
    template_name = 'products/stock_list.html'

    def get_queryset(self):
        return Stock.objects.filter(variant__product_id=self.kwargs['pid'])

    def get_context_data(self, **kwargs):
        context = super(StockListView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        context['stocks'] = Stock.objects.filter(variant__product_id=self.kwargs['pid'])
        return context

class StockCreateView(CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'products/stock_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-stock-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        context = super(StockCreateView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        context['stocks'] = Stock.objects.filter(variant__product_id=self.kwargs['pid'])
        variants = context['form'].fields["variant"].queryset.filter(product_id=self.kwargs['pid'])
        context['form'].fields["variant"].queryset = variants
        return context

class StockUpdateView(UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'products/stock_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-stock-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        context = super(StockUpdateView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        context['stocks'] = Stock.objects.filter(variant__product_id=self.kwargs['pid'])
        variants = context['form'].fields["variant"].queryset.filter(product_id=self.kwargs['pid'])
        context['form'].fields["variant"].queryset = variants
        return context

def StockDeleteView(request, pid):
    data = {}
    try:
        stock_ids = request.POST.get('stock_ids').split(',')
        variants = Stock.objects.filter(id__in=stock_ids)
        variants.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))

"""########################### PRODUCT IMAGE VIEWS ############################"""

class ProductImageView(ListView):
    template_name = 'products/image_list.html'

    def get_queryset(self):
        return ProductImage.objects.filter(variant__product_id=self.kwargs['pid'])

    def get_context_data(self, **kwargs):
        context = super(ProductImageView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        return context

class ProductImageCreateView(CreateView):
    model = ProductImage
    form_class = ProductImageForm
    template_name = 'products/image_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-image-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        context = super(ProductImageCreateView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        variants = context['form'].fields["variant"].queryset.filter(product_id=self.kwargs['pid'])
        context['form'].fields["variant"].queryset = variants
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.image = self.request.FILES['cover_image']
        self.object.save()
        image = image_cropper(self.request.POST, self.object)
        return HttpResponseRedirect(self.get_success_url())

class ProductImageUpdateView(UpdateView):
    model = ProductImage
    form_class = StockForm
    template_name = 'products/image_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-image-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        context = super(ProductImageUpdateView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        variants = context['form'].fields["variant"].queryset.filter(product_id=self.kwargs['pid'])
        context['form'].fields["variant"].queryset = variants
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.image = self.request.FILES['cover_image']
        self.object.save()
        image = image_cropper(self.request.POST, self.object)
        return HttpResponseRedirect(self.get_success_url())

def ProductImageDeleteView(request, pid):
    data = {}
    try:
        image_id = request.POST.get('image_id')
        image = ProductImage.objects.filter(id=image_id)
        image.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))



















# @csrf_exempt
# def ProductImageupload(request):
#     data = {}
#     idata = {}
#     try:file = request.FILES['cover_image']
#     except:file = request.FILES['article_image']
#     iscover = request.GET.get('cover_image',False)
#     try:
#         image = ArticleImage()
#         image.image = file
#         if iscover:
#             image.cover_image = True
#             idata['cover_image'] = True
#             data['cover'] = 1
#         image.save()
#         idata['image_obj'] = image
#         data['html']=render_to_string('articles/part_article_image.html',idata,context_instance=RequestContext(request))
#     except:pass
#     data['status'] = 1
#     return HttpResponse(json.dumps(data))

# @csrf_exempt
# def delete_article_image(request):
#     data={}
#     data['cover_img'] = False
#     id = request.POST.get('id')
#     image = ArticleImage.objects.get(id=id)
#     if image.cover_image:data['cover_img'] = True
#     image.delete()
#     data['status'] = 1
#     return HttpResponse(json.dumps(data))



# def get_attributes(request, template="products/load_attributes.html"):
#     data = {}
#     html_data = {}
#     sub_cat_ids = request.POST.get('sub_cat_ids').split(',')
#     product_id = request.POST.get('product_id')
#     if product_id:
#         product = Product.objects.get(id=product_id)
#         data['product'] = product
#     try:
#         data['attributes'] = ProductAttribute.objects.filter(category__in=sub_cat_ids)
#         html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
#         html_data['status'] = 1
#     except:
#         html_data['status'] = 0
#     return HttpResponse(json.dumps(html_data))

# def get_attribute_values(request, template="products/attribute_values.html"):
#     data = {}
#     html_data = {}
#     attr_ids = request.POST.get('attr_ids').split(',')
#     product_id = request.POST.get('product_id')
#     if product_id:
#         product = Product.objects.get(id=product_id)
#         data['product'] = product
#     try:
#         data['attributes'] = ProductAttribute.objects.filter(id__in=attr_ids)
#         html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
#         html_data['status'] = 1
#     except:
#         html_data['status'] = 0
#     return HttpResponse(json.dumps(html_data))




# class ProductDeleteView(DeleteView):
#     model = Product
#     success_url = reverse_lazy('staff-product-list')

#     # @method_decorator(login_required)
#     # def dispatch(self, *args, **kwargs):
#     #     return super(ProductDeleteView, self).dispatch(*args, **kwargs)


# class VariantCreateView(FormView):
#     form_class = VariantForm
#     template_name = 'products/variant_form.html'

#     def get_success_url(self):
#         return reverse_lazy('staff-variant-list',args=[self.kwargs['pk']])

#     def get_context_data(self, **kwargs):
#         context = super(VariantCreateView, self).get_context_data(**kwargs)
#         context['product'] = product = Product.objects.get(id=self.kwargs['pk'])
#         return context

#     def get(self, request, *args, **kwargs):
#         form = self.get_form()
#         return self.render_to_response(self.get_context_data(form=form))

#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.product = Product.objects.get(id=self.kwargs['pk'])
#         self.object.save()
#         return HttpResponseRedirect(self.get_success_url())









