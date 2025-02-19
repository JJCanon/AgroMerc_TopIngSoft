from django.urls import path 
from .views import AgroMercView
urlpatterns = [
    path('', AgroMercView.as_view(), name='AgroMerc'),
    
]