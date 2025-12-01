from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

def home(request):
    return render(request, 'store/home.html')

# -----------------------------
# Product Views
# -----------------------------
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


# -----------------------------
# Cart Views
# -----------------------------
@login_required
def cart_view(request):
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    return render(request, 'store/cart.html', {'order': order})


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if order_item.quantity < product.stock:
        order_item.quantity += 1
        order_item.save()

    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    if item.order.user != request.user:
        return redirect('cart')
    
    item.delete()
    return redirect('cart')


# -----------------------------
# Increase/Decrease Quantity Buttons
# -----------------------------
@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()

    return redirect('cart')

@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')


# -----------------------------
# Authentication Views
# -----------------------------
def signup_view(request):
    # Use Django's UserCreationForm for proper validation
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    # Use Django's AuthenticationForm for login
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            # Optional: redirect back to next page
            next_url = request.GET.get('next') or 'product_list'
            return redirect(next_url)
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('product_list')


@login_required
def checkout(request):
    order = get_object_or_404(Order, user=request.user, complete=False)

    if order.items.count() == 0:
        return redirect('cart')
    
    return render(request, 'store/checkout.html', {'order': order})


@login_required
def complete_order(request):
    order = get_object_or_404(Order, user=request.user, complete=False)

    order.complete = True
    order.save()

    Order.objects.get_or_create(user=request.user, complete=False)

    return render(request, 'store/order_complete.html', {'order': order})