from django import forms
from users.models import EcUser as User


class UserSignUpForm(forms.Form):
    username = forms.CharField(required=True,max_length=30, error_messages={'required': 'Please enter the username'},widget=forms.TextInput(attrs={'class':'form-control float-lft', 'autocomplete':'off','placeholder':'Username'}))
    first_name = forms.CharField(required=False,max_length=30, error_messages={'required': 'Please enter the first name'},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off','placeholder':'First Name'}))
    last_name = forms.CharField(required=False,max_length=30, error_messages={'required': 'Please enter the last name'},widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off','placeholder':'Last Name'}))
    email = forms.EmailField(required=True,max_length=256, error_messages={'required': 'Please enter a valid email address'},widget=forms.TextInput(attrs={'class': 'form-control float-lft', 'autocomplete':'off','placeholder':'Email Address'}))
    password = forms.CharField(required=True,max_length=100, error_messages={'required': 'Please enter the password'},widget=forms.PasswordInput(attrs={'class':'form-control', 'autocomplete':'off','placeholder':'Password'}))

    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError("The email already exists!")