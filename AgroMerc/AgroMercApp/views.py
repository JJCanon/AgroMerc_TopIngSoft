from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from .models import UserModel
from .forms import UserForm,SignInForm
# Create your views here.
class AgroMercView(TemplateView):
    template_name = 'pages/AgroMerc.html'
    
class signUpView(FormView):
    template_name = 'pages/session/signUp.html'
    form_class = UserForm
    success_url = '/signIn/'
    
    def form_valid(self, form):
         # Obtener los datos validados del formulario
        cleaned_data = form.cleaned_data
        
        # Imprimir los datos en la consola
        print("Datos ingresados por el cliente:")
        for field, value in cleaned_data.items():
            print(f"{field}: {value}")
        form.save()
        return super().form_valid(form)


class signInView(FormView):
    template_name = 'pages/session/signIn.html'
    form_class = SignInForm
    success_url = '/mainMenu/'
    
    def form_valid(self, form):
        
        username = form.cleaned_data['userName']
        password = form.cleaned_data['password']
        
        print(f"Nombre de usuario: {username}")
        print(f"Contraseña: {password}")
        
        return super().form_valid(form)
