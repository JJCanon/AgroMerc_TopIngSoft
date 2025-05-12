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
        # Filtra los elementos del carrito por el usuario actual
        return cartModel.objects.filter(user=self.request.user)


# Add to Cart View
class AddToCartView(View):
    def post(self, request, productId):
        # Obtén el producto o devuelve un error 404 si no existe
        product = get_object_or_404(ProductModel, id=productId)
        
        # Obtén la cantidad ingresada por el usuario
        quantity = int(request.POST.get('quantity', product.minQuantity))  # Valor predeterminado: cantidad mínima
        
        # Verifica si el producto ya está en el carrito del usuario
        cartItem, created = cartModel.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}  # Cantidad ingresada por el usuario
        )
        
        if not created:
            # Si el producto ya está en el carrito, incrementa la cantidad
            cartItem.quantity += quantity
            cartItem.save()
        
        # Mensaje de éxito
        messages.success(request, f'"{product.productName}" (x{quantity}) ha sido añadido al carrito.')
        
        # Redirige al usuario a la página anterior
        return redirect(request.META.get('HTTP_REFERER', 'home'))

# Edit Cart View
class EditCartProductView(View):
    def post(self,request,productId):
        cartItem = get_object_or_404(cartModel, id = productId, user=request.user)
        newQuantity = int(request.POST.get('quantity', cartItem.quantity))
        
        # Validar que la nueva cantida esté dentro del rango permitido
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
        
        # Calcular el total del carrito
        totalPrice = sum(item.totalPrice() for item in cartItems)
        
        # Renderizar la página de confirmación de pago
        return render(request, 'pages/store/shoppingCart/checkout.html', {
            'cartItems': cartItems,
            'totalPrice': totalPrice,
        })
    
    def post(self, request):
        cartItems = cartModel.objects.filter(user=request.user)
        if not cartItems.exists():
            messages.warning(request, 'No hay productos en el carrito.')
            return redirect('cart')
        
        # Crear el pedido
        totalPrice = sum(item.totalPrice() for item in cartItems)
        order = OrderModel.objects.create(
            user=request.user,
            totalPrice=totalPrice,
        )
        
        # Crear los items del pedido y actualizar las cantidades máximas
        for cartItem in cartItems:
            # Reducir la cantidad máxima del producto
            product = cartItem.product
            product.maxQuantity -= cartItem.quantity
            if product.maxQuantity < 0:  # Evitar cantidades negativas
                product.maxQuantity = 0
            product.save()
            
            # Crear el item del pedido
            OrderItemModel.objects.create(
                order=order,
                product=product,
                quantity=cartItem.quantity,
                price=product.pricePeerUnit,
            )
        
        # Vaciar el carrito
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
    pdf_generator_class = ReportLabPDFGenerator  # Nombre correcto del atributo
    
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('orderId')  # Coincide con el nombre en la URL
        order = get_object_or_404(OrderModel, id=order_id, user=request.user)
        order_items = OrderItemModel.objects.filter(order=order)
        
        # Usamos la clase directamente
        pdf_generator = self.pdf_generator_class()
        pdf_buffer = pdf_generator.generate_order_pdf(order, order_items)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orden_{order.id}.pdf"'
        return response
        
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