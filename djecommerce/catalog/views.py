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
from django.views.generic.edit import ModelFormMixin,ProcessFormView,CreateView,UpdateView, DeleteView
from django.views.generic.detail import (
    BaseDetailView, SingleObjectMixin, SingleObjectTemplateResponseMixin,DetailView,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger

from users.models import EcUser as User
from catalog.models import Catalog, CatalogCategory
from products.models import Product, ProductAttribute
from catalog.forms import CatalogForm, CatalogCategoryForm, ProductForm
from catalog.utils import image_cropper, get_unique_slug


class ProductListView(ListView):
    paginate_by = 10
    template_name = 'catalog/product_list.html'

    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super(ProductListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Product.objects.all().order_by('created_on')

    # def get_context_data(self, **kwargs):
    #     context = super(ProductListView, self).get_context_data(**kwargs)
    #     context['featured_articles'] = Product.objects.filter(created_by=self.request.user).order_by('created_on')
    #     return context






































































