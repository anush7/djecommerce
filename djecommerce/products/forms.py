from django import forms
from django.utils.translation import ugettext as _
from products.models import Product, ProductAttribute, ProductVariant, Stock, ProductImage

class ProductForm(forms.ModelForm):
    title = forms.CharField(required=True,max_length=200, error_messages={'required': 'Please enter the product title'},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    description = forms.CharField(required=True,max_length=1000, error_messages={'required': 'Please enter the product description'},widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete':'off', 'cols': 3, 'rows': 3}))
    attributes = forms.ModelMultipleChoiceField(
                    widget=forms.SelectMultiple(attrs={'class':'form-control'}),
                    required=False,
                    queryset=ProductAttribute.objects.all().order_by('name')
                )
    price = forms.DecimalField(
                required=True, 
                decimal_places=2,
                error_messages={'required': 'Please enter the product price'},
                widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
            )
    class Meta:
        model = Product
        fields = ['title', 'description', 'attributes', 'price']


class VariantForm(forms.ModelForm):
    sku = forms.SlugField(required=True,max_length=32, error_messages={'required': 'Please enter the product sku '},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    name = forms.CharField(required=False,max_length=100, error_messages={'required': 'Please enter the product title'},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    price = forms.DecimalField(
                required=False, 
                decimal_places=2,
                widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
            )
    default = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = ProductVariant
        fields = ['sku', 'name', 'price','default']

class StockForm(forms.ModelForm):
    variant = forms.ModelChoiceField(
                required=True,
                widget=forms.Select(attrs={'class':'form-control'}),
                queryset=ProductVariant.objects.all().order_by('name'),
                error_messages={'required': 'Please choose the product variant'}
            )
    quantity = forms.DecimalField(
                required=True, 
                decimal_places=2,
                error_messages={'required': 'Please choose the product variant'},
                widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
            )
    cost_price = forms.DecimalField(
                required=False, 
                decimal_places=2,
                widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
            )

    class Meta:
        model = Stock
        fields = ['variant', 'quantity', 'cost_price']

class ProductImageForm(forms.ModelForm):
    variant = forms.ModelChoiceField(
                required=True,
                widget=forms.Select(attrs={'class':'form-control'}),
                queryset=ProductVariant.objects.all().order_by('name'),
                error_messages={'required': 'Please choose the product variant'}
            )

    class Meta:
        model = ProductImage
        fields = ['variant']

