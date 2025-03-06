# urls.py
from django.urls import path
from .views import AgroMercView,SignUpView,SignInView,HomeView,CreateProductView, MyProductsView, EditProductView, DeleteProductView
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
]   