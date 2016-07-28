from django import forms
from django.utils.translation import ugettext as _
from catalog.models import Catalog, CatalogCategory
from products.models import Product, ProductAttribute, ProductAttributeValue
from django.db.models import Count
from carts.models import Tax

class CatalogForm(forms.ModelForm):
    name = forms.CharField(required=True,max_length=200, error_messages={'required': 'Please enter the catalog title'},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    description = forms.CharField(required=True,max_length=1000, error_messages={'required': 'Please enter the catalog description'},widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete':'off', 'cols': 3, 'rows': 6}))
    categories = forms.ModelMultipleChoiceField(
                        widget=forms.Select(attrs={'class':'form-control'}),
                        required=True,
                        queryset=CatalogCategory.objects.filter(parent__isnull=True).order_by('name')
                )

    class Meta:
        model = Catalog
        fields = ['name', 'description', 'categories']

class CatalogCategoryForm(forms.ModelForm):
    name = forms.CharField(required=True,max_length=200, error_messages={'required': 'Please enter the catalog category title'},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    description = forms.CharField(required=True,max_length=1000, error_messages={'required': 'Please enter the catalog category description'},widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete':'off', 'cols': 3, 'rows': 6}))
    parent = forms.ModelChoiceField(
                    widget=forms.Select(attrs={'class':'form-control'}),
                    required=False, 
                    queryset=CatalogCategory.objects.filter(parent__isnull=True).order_by('name')
            )

    class Meta:
        model = CatalogCategory
        fields = ['name', 'description', 'parent']

class AttributeForm(forms.ModelForm):
    name = forms.CharField(required=True,max_length=100, error_messages={'required': 'Please enter the attribute display name '},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    slug = forms.SlugField(required=True,max_length=50, error_messages={'required': 'Please enter the attribute intrenal name '},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))

    class Meta:
        model = ProductAttribute
        fields = ['name', 'slug']

class AttributeValueForm(forms.ModelForm):
    attribute_value = forms.CharField(required=True,max_length=100, error_messages={'required': 'Please enter the attribute value'},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))

    class Meta:
        model = ProductAttributeValue
        fields = ['attribute_value']

class TaxForm(forms.ModelForm):
    name = forms.CharField(required=True,max_length=100, error_messages={'required': 'Please enter the tax name '},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    tax_percentage = forms.DecimalField(required=True,max_digits=10, decimal_places=5, error_messages={'required': 'Please enter the tax rate '},widget=forms.NumberInput(attrs={'class':'form-control'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = Tax
        fields = ['name','tax_percentage','is_active']

    # def clean_tax_percentage(self):
    #     tax_percentage = self.cleaned_data['tax_percentage']
    #     return tax_percentage/100

