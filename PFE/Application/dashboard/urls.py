from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product, name='product'),
    path('categorie/', views.categorie, name='categorie'),
  
]


