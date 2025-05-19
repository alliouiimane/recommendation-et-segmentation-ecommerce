from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from django.db.models import Q

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from store.forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct





from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from store.models import Product
from .models import PurchaseHistory  # Importez le modèle PurchaseHistory

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # Record purchase history
        PurchaseHistory.objects.create(user=request.user, product=item.product)

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

















def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    
from .models import PurchaseHistory

# Exemple d'opération d'enregistrement
def record_purchase(user, product):
    purchase = PurchaseHistory(user=user, product=product)
    purchase.save()

from .models import PurchaseHistory

# Exemple d'appel pour enregistrer un achat
def process_purchase(request, product_id):
    # Récupérer l'utilisateur connecté (ou toute autre méthode pour obtenir l'utilisateur)
    user = request.user

    # Récupérer le produit à partir de son ID (supposons que vous ayez un modèle Product)
    product = Product.objects.get(id=product_id)

    # Enregistrer l'achat dans PurchaseHistory
    record_purchase(user, product)



# orders/views.py

from django.shortcuts import render
from .recommandation import generate_recommendations
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store.models import Product
from .models import PurchaseHistory
from django.urls import reverse
from store.models import Product

  # Assurez-vous d'importer votre fonction generate_recommendations
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from store.models import Product
from .models import PurchaseHistory



from django.urls import reverse
from accounts.models import UserProfile
from .recommandation import get_user_segment, generate_recommendations
@login_required(login_url='login')
def recommend_products_view(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        print(f"User ID: {user_id}")  # Vérifiez l'identifiant de l'utilisateur
        
        # Obtenez le mapping des clusters des utilisateurs
        user_clusters = get_user_segment(UserProfile.objects.all())
        
        if user_clusters is not None:
            # Générer les recommandations en utilisant l'ID de l'utilisateur et les clusters
            recommended_products = generate_recommendations(user_id, user_clusters)
            
            # Générer les URLs des détails de produit recommandé
            for product in recommended_products:
                product['product_url'] = reverse('product_detail', args=[product['category'].slug, product['slug']])
            
            context = {
                'recommendations': recommended_products
            }
            
            return render(request, 'store/recommendation.html', context)
        else:
            print("Erreur lors de la récupération des clusters des utilisateurs.")
            # Gérer le cas où le mapping des clusters est vide ou non disponible
            return render(request, 'error.html', {'message': "Erreur lors de la récupération des clusters des utilisateurs."})
    else:
        print("L'utilisateur n'est pas authentifié.")
        return redirect('login')  # Rediriger vers la page de connexion si l'utilisateur n'est pas authentifié
