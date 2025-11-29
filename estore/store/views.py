from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

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
    order_item.quantity += 1
    order_item.save()
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
