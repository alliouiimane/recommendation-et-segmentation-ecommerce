from django.shortcuts import render
from store.models import Product
from orders.models import Order
from accounts.models import UserProfile, Account
from orders.models import UserCluster  # Importez votre modèle UserCluster
from store.models import ReviewRating  # Importez votre modèle ReviewRating
import json

def dashboard(request):
    users_count = Account.objects.count()
    profiles_count = UserProfile.objects.count()
    orders_count = Order.objects.count()
    products_count = Product.objects.count()

    # Récupérer les informations sur les clusters d'utilisateurs
    user_clusters = UserCluster.objects.all()

    # Créer un dictionnaire pour stocker le nombre d'utilisateurs par cluster
    cluster_data = {}
    for cluster in user_clusters:
        if cluster.cluster_id in cluster_data:
            cluster_data[cluster.cluster_id] += 1
        else:
            cluster_data[cluster.cluster_id] = 1

    # Récupérer les évaluations des produits
    ratings_data = {}
    reviews = ReviewRating.objects.all()
    for review in reviews:
        rating = str(review.rating)  # Convertir le float en string pour les clés du dictionnaire
        if rating in ratings_data:
            ratings_data[rating] += 1
        else:
            ratings_data[rating] = 1

    context = {
        'users_count': users_count,
        'profiles_count': profiles_count,
        'orders_count': orders_count,
        'products_count': products_count,
        'cluster_data': json.dumps(cluster_data),  # Convertir en JSON
        'ratings_data': json.dumps(ratings_data),  # Convertir en JSON
    }
    return render(request, 'index.html', context)


from django.shortcuts import render
from store.models import Product

def product(request):
    # Récupérer tous les produits depuis la base de données
    products = Product.objects.all()

    # Définir le contexte à transmettre au template
    context = {
        'products': products,
    }

    # Rendre le template 'product.html' avec le contexte
    return render(request, 'product.html', context)
from django.shortcuts import render
from category.models import Category

def categorie(request):
    # Récupérer tous les produits depuis la base de données
    categories = Category.objects.all()

    # Définir le contexte à transmettre au template
    context = {
        'categories': categories,
    }

    # Rendre le template 'product.html' avec le contexte
    return render(request, 'categories.html', context)
