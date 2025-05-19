from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from store.models import UserSearch, ReviewRating, Product
from django.db.models import Avg
from .models import PurchaseHistory
import numpy as np
import joblib

from accounts.models import UserProfile
preprocessor = joblib.load('preprocessor.joblib')
kmeans = joblib.load('kmeans_model.joblib')
def get_user_features(user_id):
    try:
        # Retrieve user characteristics
        purchases_count = PurchaseHistory.objects.filter(user_id=user_id).count()
        search_terms_count = UserSearch.objects.filter(user_id=user_id).count()

        # Calculate average ratings given by the user
        user_ratings = ReviewRating.objects.filter(user_id=user_id)
        if user_ratings.exists():
            average_rating = user_ratings.aggregate(Avg('rating'))['rating__avg']
        else:
            average_rating = 0.0

        # Gather user characteristics into a numpy array
        user_features = np.array([purchases_count, search_terms_count, average_rating])
        return user_features

    except Exception as e:
        print(f"Une erreur s'est produite lors de la récupération des caractéristiques de l'utilisateur : {e}")
        return None
from .models import UserCluster

def get_user_segment(users):
    try:
        # Gather user features for all users
        user_features = np.array([get_user_features(user.id) for user in users])

        # Normalize user features
        user_features_scaled = preprocessor.transform(user_features)  # Utilisation du preprocessor chargé

        # Apply K-means to segment users into clusters
        user_clusters = kmeans.predict(user_features_scaled)  # Utilisation du modèle KMeans chargé

        # Map user IDs to their corresponding clusters
        user_cluster_map = {user.id: cluster for user, cluster in zip(users, user_clusters)}

        # Debugging: Print user features and assigned clusters
        for user, features in zip(users, user_features):
            cluster = user_cluster_map[user.id]
            print(f"User ID: {user.id}, Features: {features}, Cluster: {cluster}")

        # Save clusters to UserCluster model in database
        for user, cluster_id in user_cluster_map.items():
            user_cluster, created = UserCluster.objects.get_or_create(user=user)
            user_cluster.cluster_id = cluster_id
            user_cluster.save()

        return user_cluster_map

    except Exception as e:
        print(f"Une erreur s'est produite lors de la segmentation des utilisateurs : {e}")
        return {}

def generate_recommendations(user_id, user_clusters, n_recommendations=10):
    try:
        # Retrieve all available products
        all_products = Product.objects.all()

        # Retrieve the most recent purchased product by the user
        purchased_history = PurchaseHistory.objects.filter(user_id=user_id).order_by('-purchased_at').first()

        if not purchased_history or not purchased_history.product:
            print("Aucun historique d'achat trouvé pour cet utilisateur ou aucun produit acheté.")
            return []

        purchased_product = purchased_history.product

        # Check if the purchased product has a valid title
        if not purchased_product.title:
            print("Le produit acheté n'a pas de titre valide.")
            return []

        # Construct product features from titles
        product_titles = [product.title for product in all_products]

        # Initialize and fit TF-IDF model
        vectorizer = TfidfVectorizer()
        product_features_transformed = vectorizer.fit_transform(product_titles)

        # Transform purchased product title
        purchased_feature = purchased_product.title
        purchased_feature_transformed = vectorizer.transform([purchased_feature])

        # Calculate cosine similarity with all other products
        similarity_scores = cosine_similarity(purchased_feature_transformed, product_features_transformed)

        # Sort products based on cosine similarity scores
        sim_scores = list(enumerate(similarity_scores[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get indices of the top N similar products (excluding the purchased product itself)
        product_indices = [idx for idx, _ in sim_scores[:n_recommendations + 1]]

        if not product_indices:
            print("Aucun produit recommandé n'a été trouvé.")

        # Retrieve cluster of the current user
        user_cluster = user_clusters.get(user_id, "Unknown")

        # Debugging: Print recommendations with user cluster
        for i in product_indices:
            product = all_products[i]
            print(f"Recommended Product: {product.title}, Cluster: {user_cluster}")

        # Retrieve information of recommended products from Django model
        recommended_products = [
            {
                'title': all_products[i].title,
                'product_name': all_products[i].product_name,
                'category': all_products[i].category,
                'price': all_products[i].price,
                'images': all_products[i].images.url if all_products[i].images else '',  # Handle image URL
                'description': all_products[i].description,
                'slug': all_products[i].slug,
                'cluster': user_cluster  # Include user cluster in recommendations
            }
            for i in product_indices
        ]

        if recommended_products:
            print("Produits recommandés trouvés :")
            for product in recommended_products:
                print(f"- {product['title']} (Cluster: {product['cluster']})")

        return recommended_products

    except Exception as e:
        # Handle any other exceptions or errors
        print(f"Une erreur s'est produite lors de la génération des recommandations : {e}")
        return []
