from django import forms
from .models import UserModel, ProductModel
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm



class UserSignUpForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'password1', 'password2', 'fullname', 'fullLastName', 'idNumber', 'phoneNumber', 'userType']


class UserSignInForm(AuthenticationForm):
    pass


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['productName', 'specificName', 'maxQuantity', 'minQuantity', 'unit', 'pricePeerUnit']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['productName'].widget.attrs.update({'class': 'form-control'})
        self.fields['specificName'].widget.attrs.update({'class': 'form-control'})
        self.fields['maxQuantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['minQuantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['unit'].widget.attrs.update({'class': 'form-control'})
        self.fields['pricePeerUnit'].widget.attrs.update({'class': 'form-control'})
        