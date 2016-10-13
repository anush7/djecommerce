import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
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

from users.mixins import StaffRequiredMixin, StaffUpdateRequiredMixin
from users.decorators import staff_required, staff_update_required

from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger

from users.models import EcUser as User
from carts.models import Tax
from catalog.models import Catalog, CatalogCategory
from products.models import Product, ProductAttribute, ProductAttributeValue
from catalog.forms import CatalogForm, CatalogCategoryForm, AttributeForm, AttributeValueForm,TaxForm
from catalog.utils import image_cropper, get_unique_slug

"""########################### CATALOG VIEWS ############################"""
class CatalogListView(StaffRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'catalog/catalog_list.html'
    permissions = ['access_catalog']

    def get_queryset(self):
        return Catalog.objects.all().order_by('created_on')

@csrf_exempt
@staff_required(['access_catalog'])
def ajax_catalog_list(request, template='catalog/part_catalog_list.html'):
    data = {}
    html_data = {}
    key = {}
    q_text=False
    q = request.GET.get('q', False)
    status = request.GET.get('s', 'A')
    if status:key['status'] = status
    if q:q_text = (Q(name__icontains=q)|Q(description__icontains=q))

    if q_text:catalog_list = Catalog.objects.filter(q_text, **key).order_by('created_on')
    else:catalog_list = Catalog.objects.filter(**key).order_by('created_on')

    try:page = request.GET.get('page')
    except:page = 1
    paginator = Paginator(catalog_list, 10)
    try:
        catalog_list = paginator.page(page)
    except PageNotAnInteger:
        catalog_list = paginator.page(1)
    except EmptyPage:
        catalog_list = paginator.page(paginator.num_pages)

    try:next_page = catalog_list.next_page_number
    except:next_page = False

    page_obj = {
        'has_previous': catalog_list.has_previous,
        'previous_page_number' : catalog_list.previous_page_number,
        'number' : catalog_list.number,
        'paginator' : catalog_list.paginator,
        'has_next' : catalog_list.has_next,
        'next_page_number' : catalog_list.next_page_number
    }

    data['object_list'] = catalog_list
    data['page_obj'] = page_obj
    html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
    html_data['page'] = 1
    return HttpResponse(json.dumps(html_data))

class CatalogCreateView(StaffRequiredMixin, CreateView):
    model = Catalog
    form_class = CatalogForm
    success_url = reverse_lazy('staff-catalog-list')
    template_name = 'catalog/catalog_form.html'
    permissions = ['add_catalog']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = slugify(self.object.name)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())

class CatalogUpdateView(StaffUpdateRequiredMixin, UpdateView):
    model = Catalog
    form_class = CatalogForm
    success_url = reverse_lazy('staff-catalog-list')
    template_name = 'catalog/catalog_form.html'
    permissions = ['change_catalog','change_owned_catalog']

    def get_context_data(self, **kwargs):
        context = super(CatalogUpdateView, self).get_context_data(**kwargs)
        context['catalog_obj'] = self.get_object()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = slugify(self.object.name)
        self.object.modified_by = self.request.user
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())

@staff_required(['delete_catalog'])
def delete_catalog(request, pk):
    data = {}
    try:
        catalog = Catalog.objects.get(id=pk)
        catalog.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))


@staff_update_required(['change_catalog','change_owned_catalog'])
def change_catalog_status(request, pk):
    data = {}
    try:
        catalog = Catalog.objects.get(id=pk)
        if request.POST.get('status') == 'A':catalog.status = 'A'
        else:catalog.status = 'I'
        catalog.save()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))


"""############################### CATEGORY VIEWS #################################"""

class CategoryListView(StaffRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'catalog/category_list.html'
    permissions = ['access_catalogcategory']

    def get_queryset(self):
        key = {}
        key['parent__isnull'] = True
        key['status'] = 'A'
        return CatalogCategory.objects.filter(**key).prefetch_related('children').order_by('name')

@csrf_exempt
@staff_required(['access_catalogcategory'])
def ajax_category_list(request, template='catalog/part_category_list.html'):
    data = {}
    html_data = {}
    key = {}
    q_text=False
    q = request.GET.get('q', False)
    key['parent__isnull'] = True
    status = request.GET.get('s', 'A')
    if status:key['status'] = status
    if q:q_text = (Q(name__icontains=q)|Q(description__icontains=q))

    if q_text:category_list = CatalogCategory.objects.filter(q_text, **key).order_by('name')
    else:category_list = CatalogCategory.objects.filter(**key).order_by('name')

    try:page = request.GET.get('page')
    except:page = 1
    paginator = Paginator(category_list, 10)
    try:
        category_list = paginator.page(page)
    except PageNotAnInteger:
        category_list = paginator.page(1)
    except EmptyPage:
        category_list = paginator.page(paginator.num_pages)

    try:next_page = category_list.next_page_number
    except:next_page = False

    page_obj = {
        'has_previous': category_list.has_previous,
        'previous_page_number' : category_list.previous_page_number,
        'number' : category_list.number,
        'paginator' : category_list.paginator,
        'has_next' : category_list.has_next,
        'next_page_number' : category_list.next_page_number
    }

    data['object_list'] = category_list
    data['page_obj'] = page_obj
    html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
    html_data['page'] = 1
    return HttpResponse(json.dumps(html_data))

class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = CatalogCategory
    form_class = CatalogCategoryForm
    success_url = reverse_lazy('staff-category-list')
    template_name = 'catalog/category_form.html'
    permissions = ['add_catalogcategory']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = slugify(self.object.name)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class CategoryUpdateView(StaffUpdateRequiredMixin, UpdateView):
    model = CatalogCategory
    form_class = CatalogCategoryForm
    success_url = reverse_lazy('staff-category-list')
    template_name = 'catalog/category_form.html'
    permissions = ['change_catalogcategory','change_owned_catalogcategory']

    def get_context_data(self, **kwargs):
        context = super(CategoryUpdateView, self).get_context_data(**kwargs)
        context['category_obj'] = self.get_object()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = slugify(self.object.name)
        self.object.modified_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

@staff_required(['delete_catalogcategory'])
def delete_category(request, pk):
    data = {}
    try:
        category = CatalogCategory.objects.get(id=pk)
        category.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))

@staff_update_required(['change_catalogcategory','change_owned_catalogcategory'])
def change_category_status(request, pk):
    data = {}
    try:
        category = CatalogCategory.objects.get(id=pk)
        if request.POST.get('status') == 'A':category.status = 'A'
        else:category.status = 'I'
        category.save()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))


"""############################### ATTRIBUTES VIEWS #################################"""

class AttributeListView(StaffRequiredMixin, ListView):
    paginate_by = 5
    template_name = 'catalog/attribute_list.html'
    permissions = ['access_productattribute']

    def get_context_data(self, **kwargs):
        context = super(AttributeListView, self).get_context_data(**kwargs)
        context['categories'] = pcats = CatalogCategory.objects.annotate(nsubcats=Count('children')).filter(
                                        parent__isnull=True,
                                        nsubcats__gt=0
                                ).order_by('name')
        if pcats:
            context['sub_cats'] = scats = CatalogCategory.objects.filter(
                                    parent=pcats[0],
                                ).order_by('name')
        return context

    def get_queryset(self):
        return ProductAttribute.objects.filter(status='A').order_by('name')

@csrf_exempt
@staff_required(['access_productattribute'])
def ajax_attribute_list(request, template='catalog/part_attribute_list.html'):
    data = {}
    html_data = {}
    key = {}
    q_text=False
    q = request.GET.get('q', False)
    category_id = request.GET.get('c', False)
    status = request.GET.get('s', 'A')
    if status:key['status'] = status

    if q:key['name__icontains']=q

    attribute_list = ProductAttribute.objects.filter(**key).order_by('name')

    try:page = request.GET.get('page')
    except:page = 1
    paginator = Paginator(attribute_list, 5)
    try:
        attribute_list = paginator.page(page)
    except PageNotAnInteger:
        attribute_list = paginator.page(1)
    except EmptyPage:
        attribute_list = paginator.page(paginator.num_pages)

    try:next_page = attribute_list.next_page_number
    except:next_page = False

    page_obj = {
        'has_previous': attribute_list.has_previous,
        'previous_page_number' : attribute_list.previous_page_number,
        'number' : attribute_list.number,
        'paginator' : attribute_list.paginator,
        'has_next' : attribute_list.has_next,
        'next_page_number' : attribute_list.next_page_number
    }

    data['object_list'] = attribute_list
    data['page_obj'] = page_obj
    html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
    html_data['page'] = 1
    return HttpResponse(json.dumps(html_data))

class AttributeCreateView(StaffRequiredMixin, CreateView):
    model = ProductAttribute
    form_class = AttributeForm
    success_url = reverse_lazy('staff-attribute-list')
    template_name = 'catalog/attribute_form.html'
    permissions = ['add_productattribute']

    def get_context_data(self, **kwargs):
        context = super(AttributeCreateView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.modified_by = self.request.user
        self.object.save()
        attr_vals = self.request.POST.getlist('attr_vals')
        for val in attr_vals:
            ProductAttributeValue.objects.create(attribute_value=val,attribute=self.object)

        return HttpResponseRedirect(self.get_success_url())

class AttributeUpdateView(StaffUpdateRequiredMixin, UpdateView):
    model = ProductAttribute
    form_class = AttributeForm
    success_url = reverse_lazy('staff-attribute-list')
    template_name = 'catalog/attribute_form.html'
    permissions = ['change_productattribute','change_owned_productattribute']

    def get_context_data(self, **kwargs):
        context = super(AttributeUpdateView, self).get_context_data(**kwargs)
        context['attribute_obj'] = attribute_obj = self.get_object()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.modified_by = self.request.user
        self.object.save()
        attr_vals = self.request.POST.getlist('attr_vals')
        for val in attr_vals:
            ProductAttributeValue.objects.create(attribute_value=val,attribute=self.object)
        return HttpResponseRedirect(self.get_success_url())

@staff_required(['delete_productattribute'])
def delete_attribute(request, pk):
    data = {}
    try:
        attribute = ProductAttribute.objects.get(id=pk)
        attribute.delete()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))

@staff_update_required(['change_productattribute','change_owned_productattribute'])
def change_attribute_status(request, pk):
    data = {}
    try:
        attribute = ProductAttribute.objects.get(id=pk)
        if request.POST.get('status') == 'A':attribute.status = 'A'
        else:attribute.status = 'I'
        attribute.save()
        data['status'] = 1
    except:data['status'] = 0
    return HttpResponse(json.dumps(data))

def get_list_sub_cats(request, template="catalog/load_list_subcats.html"):
    data = {}
    html_data = {}
    pk = request.POST.get('pid')
    try:
        parent_cat = CatalogCategory.objects.get(id=pk)
        subcats = parent_cat.children.all()
        data['sub_cats'] = subcats
        html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
        html_data['status'] = 1
    except:
        html_data['status'] = 0
    return HttpResponse(json.dumps(html_data))

def get_sub_cats(request, template="catalog/load_subcats.html"):
    data = {}
    html_data = {}
    pk = request.POST.get('pid')
    try:
        parent_cat = CatalogCategory.objects.get(id=pk)
        subcats = parent_cat.children.all()
        data['sub_cats'] = subcats
        html_data['html'] = render_to_string(template,data,context_instance=RequestContext(request))
        html_data['status'] = 1
    except:
        html_data['status'] = 0
    return HttpResponse(json.dumps(html_data))


"""#################################################################################################"""


class TaxListView(StaffRequiredMixin, ListView):
    template_name = 'catalog/tax_list.html'
    permissions = ['access_tax']

    def get_queryset(self):
        return Tax.objects.all().order_by('name')

class TaxFormView(StaffRequiredMixin, FormView):
    template_name = 'catalog/tax_form.html'
    form_class = TaxForm
    success_url = reverse_lazy('staff-tax-list')
    permissions = ['add_tax']

    def get_form_kwargs(self):
        kwargs = super(TaxFormView, self).get_form_kwargs()
        if self.kwargs.get('pk'):
            tax = Tax.objects.get(id=self.kwargs.get('pk'))
            kwargs.update({'instance': tax})
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

class TaxDeleteView(StaffRequiredMixin, View):
    permissions = ['delete_tax']

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            data = {}
            try:
                tax = Tax.objects.get(id=kwargs['pk'])
                tax.delete()
                data['status'] = 1
            except:data['status'] = 0
            return JsonResponse(data)
        else:
            raise Http404


# class AttributeFormView(FormView):
#     form_class = AttributeForm
#     success_url = reverse_lazy('staff-attribute-list')
#     template_name = 'catalog/attribute_form.html'

#     def get(self, request, *args, **kwargs):
#         form = self.get_form()
#         return self.render_to_response(self.get_context_data(form=form))

#     def post(self, request, *args, **kwargs):
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)






# class AttributeFormView(TemplateResponseMixin, ProcessFormView):
#     template_name = 'catalog/attribute_form.html'

#     def render_to_response(self, context, **response_kwargs):
#         print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
#         print context
#         print response_kwargs
#         print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
#         """
#         Returns a response, using the `response_class` for this
#         view, with a template rendered with the given context.
#         If any keyword arguments are provided, they will be
#         passed to the constructor of the response class.
#         """
#         response_kwargs.setdefault('content_type', self.content_type)
#         return self.response_class(
#             request=self.request,
#             template=self.get_template_names(),
#             context=context,
#             using=self.template_engine,
#             **response_kwargs
#         )

#     def get(self, request, *args, **kwargs):
#         attr_form = AttributeForm()
#         attr_val_form = AttributeValueForm()
#         forms = {'attr_form':attr_form,'attr_val_form':attr_val_form}
#         return self.render_to_response({}, forms)

#     def post(self, request, *args, **kwargs):
#         attr_form = AttributeForm(request.POST)
#         attr_val_form = AttributeValueForm(request.POST)

#         if attr_form.is_valid() and attr_val_form.is_valid():
#             return HttpResponseRedirect(reverse('staff-attribute-list'))
#         else:
#             forms = {'attr_form':attr_form,'attr_val_form':attr_val_form}
#             return self.render_to_response(self.get_context_data(forms))



































































































































