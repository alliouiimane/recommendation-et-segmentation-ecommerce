from django.contrib import admin
from .models import Product, Variation, ReviewRating

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')


from django.contrib import admin
from .models import UserSearch

class UserSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'keyword', 'search_date')  # Champs à afficher dans la liste
    search_fields = ('user__username', 'keyword')  # Champs de recherche
    list_filter = ('user', 'search_date')  # Filtres latéraux

# Enregistrer le modèle UserSearch avec l'admin personnalisé
admin.site.register(UserSearch, UserSearchAdmin)


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)


