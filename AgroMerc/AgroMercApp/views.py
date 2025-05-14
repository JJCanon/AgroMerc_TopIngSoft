from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, View
from .forms import UserSignUpForm, UserSignInForm, ProductForm
from .models import OrderModel, OrderItemModel, UserModel, ProductModel, cartModel
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .services.pdf_service import ReportLabPDFGenerator
from .models import ProductModel, FavoriteProduct
import requests

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
        queryset = ProductModel.objects.all()

        if self.request.user.userType == 'seller':
            queryset = queryset.exclude(seller=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unique_categories = sorted(set(cat for sub in CATEGORIES.values() for cat in sub))
        context['categorias'] = unique_categories
        
        User = get_user_model()
        context['sellers'] = User.objects.filter(productmodel__isnull=False).distinct()
        
        context['favorites_ids'] = set(FavoriteProduct.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        return context
    
# Create Product View
class CreateProductView(LoginRequiredMixin, CreateView):
    model = ProductModel
    form_class = ProductForm
    template_name = 'pages/store/products/createProducts.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.sellerId = self.request.user.idNumber
        productName = form.cleaned_data['productName']
        
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
        products = ProductModel.objects.all()
        query = self.request.GET.get('q', '')
        category = self.request.GET.get('categoria', '')
        seller = self.request.GET.get('seller', '')

        if query:
            products = products.filter(productName__icontains=query)
        if category:
            filtred_products = [
                name for name, categories in CATEGORIES.items() if category in categories
            ]
            products = products.filter(productName__in=filtred_products)
        if seller:
            products = products.filter(seller__username=seller)
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '') 
        context['selected_category'] = self.request.GET.get('categoria', '')
        context['selected_seller'] = self.request.GET.get('seller', '')

        unique_categories = sorted(set(cat for sub in CATEGORIES.values() for cat in sub))
        context['categorias'] = unique_categories
        
        User = get_user_model()
        context['sellers'] = User.objects.filter(productmodel__isnull=False).distinct()
        return context


# Cart view
class CartView(LoginRequiredMixin, ListView):
    model = cartModel
    template_name = 'pages/store/shoppingCart/shoppingCart.html'
    context_object_name = 'cartItems'

    def get_queryset(self):
        return cartModel.objects.filter(user=self.request.user)


# Add to Cart View
class AddToCartView(View):
    def post(self, request, productId):
        product = get_object_or_404(ProductModel, id=productId)
        quantity = int(request.POST.get('quantity', product.minQuantity))
        
        cartItem, created = cartModel.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cartItem.quantity += quantity
            cartItem.save()
        
        messages.success(request, f'"{product.productName}" (x{quantity}) ha sido añadido al carrito.')
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))

# Edit Cart View
class EditCartProductView(View):
    def post(self,request,productId):
        cartItem = get_object_or_404(cartModel, id = productId, user=request.user)
        newQuantity = int(request.POST.get('quantity', cartItem.quantity))
        
        if newQuantity < cartItem.product.minQuantity:
            messages.error(request,f'la cantidad mínima permitida es {cartItem.product.minQuantity}.')
        elif newQuantity > cartItem.product.maxQuantity:
            messages.error(request,f'la cantidad máxima permitida es {cartItem.product.maxQuantity}.')
        else:
            cartItem.quantity = newQuantity
            cartItem.save()
            messages.success(request,f'La cantidad de "{cartItem.product.productName}" ha sido actualizada a {newQuantity}.')
            
        return redirect('cart')

# Delete Cart View
class DeleteCartProductView(View):
    def post(self,request,productId):
        cartItem = get_object_or_404(cartModel, id = productId, user=request.user)
        cartItem.delete()
        messages.success(request,f'"{cartItem.product.productName}" ha sido eliminado del carrito.')
        return redirect('cart')

# Confirmation Pay View
class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cartItems = cartModel.objects.filter(user=request.user)
        if not cartItems.exists():
            messages.warning(request, 'No hay productos en el carrito.')
            return redirect('cart')
        
        totalPrice = sum(item.totalPrice() for item in cartItems)
        
        return render(request, 'pages/store/shoppingCart/checkout.html', {
            'cartItems': cartItems,
            'totalPrice': totalPrice,
        })
    
    def post(self, request):
        cartItems = cartModel.objects.filter(user=request.user)
        if not cartItems.exists():
            messages.warning(request, 'No hay productos en el carrito.')
            return redirect('cart')
        
        totalPrice = sum(item.totalPrice() for item in cartItems)
        order = OrderModel.objects.create(
            user=request.user,
            totalPrice=totalPrice,
        )
        
        for cartItem in cartItems:
            product = cartItem.product
            product.maxQuantity -= cartItem.quantity
            if product.maxQuantity < 0:
                product.maxQuantity = 0
            product.save()
            
            OrderItemModel.objects.create(
                order=order,
                product=product,
                quantity=cartItem.quantity,
                price=product.pricePeerUnit,
            )
            
        cartItems.delete()
        messages.success(request, 'Pedido realizado con éxito.')
        
        return redirect('orderConfirmation', orderId=order.id)

# Order Confirmation View
class OrderConfirmationView(LoginRequiredMixin, View):
    def get(self, request, orderId):
        order = get_object_or_404(OrderModel, id=orderId, user=request.user)
        return render(request, 'pages/store/shoppingCart/orderConfirmation.html', {
            'order': order,
        })
        

# PDF Generation View
class OrderPDFDownloadView(LoginRequiredMixin, View):
    pdf_generator_class = ReportLabPDFGenerator
    
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('orderId')
        order = get_object_or_404(OrderModel, id=order_id, user=request.user)
        order_items = OrderItemModel.objects.filter(order=order)
        
        pdf_generator = self.pdf_generator_class()
        pdf_buffer = pdf_generator.generate_order_pdf(order, order_items)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orden_{order.id}.pdf"'
        return response
    
class AddToFavoritesView(LoginRequiredMixin, View):
    def post(self, request, productId):
        product = get_object_or_404(ProductModel, id=productId)
        _, created = FavoriteProduct.objects.get_or_create(user=request.user, product=product)

        if created:
            messages.success(request, f'"{product.productName}" ha sido añadido a tus favoritos.')
        else:
            messages.info(request, f'"{product.productName}" ya está en tus favoritos.')

        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('home')))


class RemoveFromFavoritesView(LoginRequiredMixin, View):
    def post(self, request, productId):
        product = get_object_or_404(ProductModel, id=productId)
        FavoriteProduct.objects.filter(user=request.user, product=product).delete()

        messages.success(request, f'"{product.productName}" ha sido eliminado de tus favoritos.')
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('home')))


class ListFavoritesView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    template_name = 'pages/store/products/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return FavoriteProduct.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = [fav.product for fav in context['favorites']]
        return context
    
class ProductosAliadosView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/store/products/aliados.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            response = requests.get('http://localhost:8000/api/products')
            response.raise_for_status()
            print('Respuesta de API de aliados:',   response.json())
            context['aliados'] = response.json()
        except requests.RequestException:
            context['aliados'] = []
            context['error'] = 'No se pudo obtener la información de productos aliados.'

        return context
    
class GoogleBooksView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/external/books.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url = 'https://www.googleapis.com/books/v1/volumes?q=agricultura'
        try:
            response = requests.get(url)
            response.raise_for_status()
            books_data = response.json()
            context['books'] = books_data.get('items', [])
        except requests.RequestException:
            context['books'] = []
            context['error'] = 'No se pudieron obtener los libros en este momento.'
        return context


#Diccionarios

# Categorias de productos
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