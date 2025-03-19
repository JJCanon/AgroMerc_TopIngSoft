from django.shortcuts import render, redirect
from django.views.generic import TemplateView,CreateView,ListView,UpdateView,DeleteView
from .forms import UserSignUpForm, UserSignInForm, ProductForm
from .models import UserModel, ProductModel
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin


# AgroMerc View
class AgroMercView(TemplateView):
    template_name = 'pages/AgroMerc.html'


#Sign Up View
class SignUpView(CreateView):
    model = UserModel
    form_class = UserSignUpForm
    template_name = 'pages/session/signUp.html'
    success_url = reverse_lazy('signIn')
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario registrado correctamente')
        return super().form_valid(form)
    
#Sign In View
class SignInView(LoginView):
    template_name = 'pages/session/signIn.html'
    form_class = UserSignInForm
    success_url = reverse_lazy('home')
    
    
# Home View
class HomeView(LoginRequiredMixin, ListView):
    model = ProductModel
    template_name = 'pages/store/home.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # Obtén todos los productos
        queryset = ProductModel.objects.all()

        # Si el usuario es un Seller, excluye sus propios productos
        if self.request.user.userType == 'seller':
            queryset = queryset.exclude(seller=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context['products'])  # Imprime los productos en la consola (para depuración)
        return context
    
# Create Product View
class CreateProductView(LoginRequiredMixin, CreateView):
    model = ProductModel
    form_class = ProductForm
    template_name = 'pages\store\products\createProducts.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        form.instance.seller = self.request.user #asignar el usuario actual al campo seller
        form.instance.sellerId = self.request.user.idNumber #asignar la cedula del usuario actual al campo sellerId
        productName = form.cleaned_data['productName'] #obtener el nombre del producto
        
        #asignar categorias a los productos
        if productName in CATEGORIES:
            form.instance.categories = ','.join(CATEGORIES[productName])
        return super().form_valid(form)
    
    
# My Products View
class MyProductsView(LoginRequiredMixin, ListView):
    model = ProductModel
    template_name = 'pages/store/products/myProducts.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return ProductModel.objects.filter(seller=self.request.user)

# Edit Product View
class EditProductView(LoginRequiredMixin, UpdateView):
    model = ProductModel
    form_class = ProductForm
    template_name = 'pages/store/products/editProducts.html' 
    success_url = reverse_lazy('myProducts')
    
    def get_queryset(self):
        return ProductModel.objects.filter(seller=self.request.user)
    
# Delete Product View
class DeleteProductView(LoginRequiredMixin, DeleteView):
    model = ProductModel
    template_name = 'pages/store/products/deleteProducts.html'
    success_url = reverse_lazy('myProducts')
    
    def get_queryset(self):
        return ProductModel.objects.filter(seller=self.request.user)
    
class SearchProductView(LoginRequiredMixin, ListView):
    model = ProductModel
    template_name = 'pages/store/home.html'  
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return ProductModel.objects.filter(productName__icontains=query)
        return ProductModel.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '') 
        return context

#Diccionarios

#categorias de productos
# Diccionario de categorías
CATEGORIES = {
    'aguacate': ['Frutas tropicales', 'Fuentes de fibra'],
    'banana': ['Frutas tropicales', 'Fuentes de fibra'],
    'brocoli': ['Hortalizas', 'Verduras crucíferas', 'Fuentes de fibra'],
    'cafe': ['Granos'],
    'cebolla_cabezona': ['Hortalizas', 'Verduras crucíferas', 'Fuentes de fibra'],
    'cebolla_larga': ['Hortalizas', 'Verduras crucíferas', 'Fuentes de fibra'],
    'coliflor': ['Hortalizas', 'Verduras crucíferas'],
    'frijol': ['Legumbres', 'Fuentes de fibra', 'Granos'],
    'guayaba': ['Frutas tropicales', 'Fuentes de fibra'],
    'lechuga': ['Hortalizas', 'Fuentes de fibra'],
    'limon': ['Frutas tropicales', 'Cítricos'],
    'lulo': ['Frutas tropicales', 'Cítricos'],
    'maiz': ['Legumbres', 'Fuentes de fibra', 'Granos'],
    'mango': ['Frutas tropicales'],
    'maracuya': ['Frutas tropicales', 'Cítricos'],
    'naranja': ['Frutas tropicales', 'Cítricos'],
    'papa': ['Hortalizas', 'Tubérculos', 'Fuentes de fibra'],
    'papaya': ['Frutas tropicales'],
    'platano': ['Frutas tropicales'],
    'piña': ['Frutas tropicales'],
    'sandia': ['Frutas tropicales'],
    'tomate': ['Hortalizas', 'Fuentes de fibra'],
    'yuca': ['Hortalizas', 'Tubérculos', 'Fuentes de fibra'],
    'zanahoria': ['Hortalizas', 'Tubérculos', 'Fuentes de fibra']
}