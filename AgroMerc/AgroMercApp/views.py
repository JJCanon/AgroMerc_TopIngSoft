from django.shortcuts import render
from django.views.generic import TemplateView
from .models import UserModel
from .forms import UserForm
# Create your views here.
class AgroMercView(TemplateView):
    template_name = 'pages/AgroMerc.html'
    
class signUpView(TemplateView):
    template_name = 'pages/signUp.html'
    
    
