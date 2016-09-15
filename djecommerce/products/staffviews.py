import json
import csv
from datetime import datetime
from django.contrib import messages
from django.utils.six.moves import range
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, render_to_response, get_list_or_404,get_object_or_404
from django.template.loader import render_to_string
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.template.defaultfilters import slugify

from django.views.generic.list import ListView
from django.views.generic import View, TemplateView
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
from catalog.mixins import StaffRequiredMixin, LoginRequiredMixin, staff_required
from django.contrib.admin.views.decorators import staff_member_required
from products.models import Product, ProductAttribute, ProductCategory, ProductAttributeValue, ProductVariant, Stock, ProductImage
from products.forms import ProductForm, VariantForm, StockForm, ProductImageForm
from products.utils import image_cropper, get_unique_slug, get_rows

class ProductListView(StaffRequiredMixin, ListView):
    paginate_by = 1
    template_name = 'products/product_list.html'

    def get_queryset(self):
        return Product.objects.filter(status='A').order_by('created_on')

@csrf_exempt
@staff_required
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
    paginator = Paginator(product_list, 1)
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

class ProductCreateView(StaffRequiredMixin, CreateView):
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

class ProductUpdateView(StaffRequiredMixin, UpdateView):
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

@staff_required
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

@staff_required
def get_sub_cats(request, template="products/load_sub_cats.html"):
    data = {}
    html_data = {}
    pk = request.POST.get('pid')
    product_id = request.POST.get('product_id')
    import_page = request.POST.get('import_page')
    if product_id:
        product = Product.objects.get(id=product_id)
        data['product'] = product
    if import_page:
        data['import_page'] = True
    try:
        parent_cat = CatalogCategory.objects.get(id=pk)
        data['sub_cats'] = parent_cat.children.all()
        html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
        html_data['status'] = 1
    except:
        html_data['status'] = 0
    return HttpResponse(json.dumps(html_data))

"""########################### VARIANTS VIEWS ############################"""

class VariantListView(StaffRequiredMixin, ListView):
    template_name = 'products/variant_list.html'

    def get_queryset(self):
        return ProductVariant.objects.filter(product_id=self.kwargs['pid']).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(VariantListView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        return context

class VariantCreateView(StaffRequiredMixin, CreateView):
    model = ProductVariant
    form_class = VariantForm
    template_name = 'products/variant_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-variant-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        product = Product.objects.get(id=self.kwargs['pid'])
        self.initial = {'price':product.price}
        context = super(VariantCreateView, self).get_context_data(**kwargs)
        context['product'] = product
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

class VariantUpdateView(StaffRequiredMixin, UpdateView):
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

@staff_required
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

class StockListView(StaffRequiredMixin, ListView):
    template_name = 'products/stock_list.html'

    def get_queryset(self):
        return Stock.objects.filter(variant__product_id=self.kwargs['pid'])

    def get_context_data(self, **kwargs):
        context = super(StockListView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        context['stocks'] = Stock.objects.filter(variant__product_id=self.kwargs['pid'])
        return context

class StockCreateView(StaffRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'products/stock_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-stock-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        product = Product.objects.get(id=self.kwargs['pid'])
        self.initial = {'cost_price':product.price,'quantity_allocated':0}
        context = super(StockCreateView, self).get_context_data(**kwargs)
        context['product'] = product
        context['stocks'] = Stock.objects.filter(variant__product_id=self.kwargs['pid'])
        variants = context['form'].fields["variant"].queryset.annotate(nstocks=Count('stocks'))\
                        .filter(product_id=self.kwargs['pid'],nstocks=0)
        context['form'].fields["variant"].queryset = variants
        return context

class StockUpdateView(StaffRequiredMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'products/stock_form.html'

    def get_success_url(self):
        return reverse_lazy('staff-stock-list',args=[self.kwargs['pid']])

    def get_context_data(self, **kwargs):
        context = super(StockUpdateView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        context['stocks'] = Stock.objects.filter(variant__product_id=self.kwargs['pid'])
        variants = context['form'].fields["variant"].queryset.annotate(nstocks=Count('stocks'))\
                        .filter((Q(nstocks=0)|Q(stocks=context['object'])),product_id=self.kwargs['pid']).distinct()
        context['form'].fields["variant"].queryset = variants
        return context

@staff_required
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

class ProductImageView(StaffRequiredMixin, ListView):
    template_name = 'products/image_list.html'

    def get_queryset(self):
        return ProductImage.objects.filter(variant__product_id=self.kwargs['pid'])

    def get_context_data(self, **kwargs):
        context = super(ProductImageView, self).get_context_data(**kwargs)
        context['product'] = product = Product.objects.get(id=self.kwargs['pid'])
        return context

class ProductImageCreateView(StaffRequiredMixin, CreateView):
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

class ProductImageUpdateView(StaffRequiredMixin, UpdateView):
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

@staff_required
def ProductImageDeleteView(request, pid):
    data = {}
    try:
        image_id = request.POST.get('image_id')
        image = ProductImage.objects.filter(id=image_id)
        image.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))

"""################################ PRODUCT IMPORT EXPORT ############################"""

class Echo(object):
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

class ProductImportView(StaffRequiredMixin, TemplateView):
    template_name = 'products/import.html'

    def get_context_data(self, **kwargs):
        context = super(ProductImportView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        if not request.POST.getlist('category'):
            messages.error(request, "Please select a category")
            return render(request, self.template_name, {})

        try:csvfile = request.FILES['csvfile']
        except:
            messages.error(request, "Please select a file to import")
            return render(request, self.template_name, {})

        req_fields = ['title','description','price','rating','status']
        python_csv_object = csv.DictReader(csvfile.read().splitlines())
        new_product = Product()
        for i, rowData in enumerate(python_csv_object):
            row = {}
            for k in rowData.keys():row[k.replace(' ','_').lower()] = rowData[k]
            if i == 0:
                if not all(map(lambda v: v in row.keys(), req_fields)):
                    messages.error(request, "Required Columns not available")
                    return render(request, self.template_name, {})

            for field in req_fields:
                setattr(new_product, field, row[field])

            new_product.created_by = request.user
            new_product.save()
            subcat_ids = self.request.POST.getlist('category')
            if subcat_ids:
                ProductCategory.objects.filter(product=self.object).delete()
                for cid in subcat_ids:
                    subcat = CatalogCategory.objects.get(id=cid)
                    ProductCategory.objects.create(product=new_product, category=subcat)

        messages.success(request, "Import Complete")
        return render(request, self.template_name, {})

class ProductExportView(StaffRequiredMixin, TemplateView):
    template_name = 'products/export.html'

@staff_required
def ProductExportCsv(request):
    cats = []
    key= {}
    fields = ['title','description','price','rating']
    
    pseudo_buffer = Echo()
    catids = request.GET.get('cats',False)
    if catids:cats = catids.split(',')
    cats = CatalogCategory.objects.filter(id__in=cats)
    if cats:key['categories__in']=cats

    queryset = Product.objects.filter(status='A',**key)
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in get_rows(queryset, fields)), content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="products-%s.csv"' % datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    return response

















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









