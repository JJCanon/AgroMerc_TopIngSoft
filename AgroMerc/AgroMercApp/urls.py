from django.urls import path 
from .views import AgroMercView,signUpView,signInView
urlpatterns = [
    path('', AgroMercView.as_view(), name='AgroMerc'),
    path('signUp/', signUpView.as_view(), name='signUp'),
    path('signIn/', signInView.as_view(), name='signIn'),
]