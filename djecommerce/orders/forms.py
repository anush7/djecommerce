from django import forms
from .models import UserAddress
from users.models import EcUser as User

class MyModelChoiceField(forms.ModelChoiceField):
    def get_instance_id(self, obj):
        return str(obj.id)

class AddressForm(forms.Form):
	billing_address = forms.ModelChoiceField(
			queryset=UserAddress.objects.filter(type="billing"),
			widget = forms.RadioSelect(attrs={'class':'pull-left','style':'margin-right:5px;margin-top:1px;'}),
			empty_label = None
			)
	shipping_address = MyModelChoiceField(
		queryset=UserAddress.objects.filter(type="shipping"),
		widget = forms.RadioSelect(attrs={'class':'pull-left','style':'margin-right:5px;margin-top:1px;'}),
		empty_label = None
		)

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
	default = forms.BooleanField(required=False, widget=forms.CheckboxInput())
	type = forms.ChoiceField(
		choices=ADDRESS_TYPE, 
		widget=forms.Select(attrs={'class':'form-control'})
		)

	class Meta:
		model = UserAddress
		fields = [
			'street',
			'city',
			'state',
			'zipcode',
			'type'
		]