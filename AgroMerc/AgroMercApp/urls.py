# urls.py
from django.urls import path
from .views import AgroMercView,SignUpView,SignInView,HomeView,CreateProductView,MyProductsView,EditProductView,DeleteProductView,SearchProductView,AddToCartView,CartView,EditCartProductView,DeleteCartProductView,CheckoutView,OrderConfirmationView, OrderPDFDownloadView
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('',AgroMercView.as_view(),name='AgroMerc'),
    path('signUp/', SignUpView.as_view(), name='signUp'),
    path('signIn/', SignInView.as_view(), name='signIn'),
    path('signOut/', LogoutView.as_view(), name='signOut'),
    path('home/', HomeView.as_view(), name='home'),
    path('createProduct/', CreateProductView.as_view(), name='createProduct'),
    path('myProducts/', MyProductsView.as_view(), name='myProducts'),
    path('editProducto/<int:pk>/', EditProductView.as_view(), name='editProduct'),
    path('deleteProduct/<int:pk>/', DeleteProductView.as_view(), name='deleteProduct'),
    path('searchProduct/', SearchProductView.as_view(), name='searchProduct'),
    path('shoppingCart/', CartView.as_view(), name='cart'),
    path('addToCart/<int:productId>/', AddToCartView.as_view(), name='addToCart'),
    path('editCartProduct/<int:productId>/', EditCartProductView.as_view(), name='editCartProduct'),
    path('deleteCartProduct/<int:productId>/', DeleteCartProductView.as_view(), name='deleteCartProduct'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orderConfirmation/<int:orderId>/', OrderConfirmationView.as_view(), name='orderConfirmation'),
    path('order/<int:orderId>/download/',OrderPDFDownloadView.as_view(), name='downLoadOrderPDF'),
]  