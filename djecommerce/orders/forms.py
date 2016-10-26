from django import forms
from .models import UserAddress, Shipping
from users.models import EcUser as User


ADDRESS_TYPE = (
	('billing', 'Billing'),
	('shipping', 'Shipping'),
)

class UserAddressForm(forms.ModelForm):
	street = forms.CharField(
				required=True,max_length=200, error_messages={'required': 'Please enter the street name/number'},
				widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
			)
	city = forms.CharField(
				required=True,max_length=200, error_messages={'required': 'Please enter the street name/number'},
				widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
			)
	state = forms.CharField(
				required=True,max_length=200, error_messages={'required': 'Please enter the street name/number'},
				widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
			)
	zipcode = forms.CharField(
				required=True,max_length=200, error_messages={'required': 'Please enter the street name/number'},
				widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'})
			)
	default = forms.BooleanField(
				required=False, widget=forms.CheckboxInput()
			)
	type = forms.ChoiceField(
				choices=ADDRESS_TYPE, 
				widget=forms.Select(attrs={'class':'form-control'})
			)

	class Meta:
		model = UserAddress
		fields = ['street', 'city', 'state', 'zipcode', 'default', 'type']



class ShippingForm(forms.ModelForm):
    name = forms.CharField(required=False,max_length=100, error_messages={'required': 'Please enter the shipping name '},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    rate = forms.DecimalField(required=True,max_digits=10, decimal_places=5, error_messages={'required': 'Please enter the shipping rate '},widget=forms.NumberInput(attrs={'class':'form-control'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = Shipping
        fields = ['name','rate','is_active']
















# Not Using the form

# class AddressForm(forms.Form):
# 	billing_address = forms.ModelChoiceField(
# 						queryset=UserAddress.objects.filter(type="billing"),
# 						widget = forms.RadioSelect(
# 							attrs={'class':'pull-left','style':'margin-right:5px;margin-top:1px;'}
# 						),
# 						empty_label = None
# 					)
# 	shipping_address = forms.ModelChoiceField(
# 						queryset=UserAddress.objects.filter(type="shipping"),
# 						widget = forms.RadioSelect(
# 							attrs={'class':'pull-left','style':'margin-right:5px;margin-top:1px;'}
# 						),
# 						empty_label = None
# 					)