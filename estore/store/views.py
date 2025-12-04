from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


# -----------------------------
# Home Page
# -----------------------------
def home(request):
    """
    Landing page with the hero section
    """
    return render(request, 'store/home.html')


# -----------------------------
# Product Views
# -----------------------------
def product_list(request):
    """
    Show all available products
    """
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, pk):
    """
    Display a single product's details
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


# -----------------------------
# Cart Views
# -----------------------------
@login_required
def cart_view(request):
    """
    Get the active order for the logged in user.
    If none exists, a new one is created automatically
    """
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    return render(request, 'store/cart.html', {'order': order})


@login_required
def add_to_cart(request, pk):
    """
    Add a product to the user's cart.
    If the item already exists, you can decrease or increase the quantity (up to the stock limit)
    """
    product = get_object_or_404(Product, pk=pk)
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if order_item.quantity < product.stock:
        order_item.quantity += 1
        order_item.save()

    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """
    Remove an item from the cart entirely.
    Security check will ensure user can't remove items from another user's cart
    """
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
    """
    Increase the quantity of a specific cart item.
    Cannot exceed available stock
    """
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()

    return redirect('cart')

@login_required
def decrease_quantity(request, item_id):
    """
    Decrease the quantity of a specific cart item.
    If user decreases to less than 1, the item get removed from the cart
    """
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
    """
    Create a new user account and logs them in immediately.
    Uses Django's built-in UserCreationForm
    """
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    """
    Logs a user in using Django's built-in AuthenticationForm.
    Supports ?next= URL redirect after authentication
    """
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.GET.get('next') or 'product_list'
            return redirect(next_url)
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    """
    Logs the user out and redirects back to product list
    """
    logout(request)
    return redirect('product_list')



# -----------------------------
# Checkout and Order Completion
# -----------------------------
@login_required
def checkout(request):
    """
    Show checkout summary.
    Redirect user back to cart if it's empty
    """
    order = get_object_or_404(Order, user=request.user, complete=False)

    if order.items.count() == 0:
        return redirect('cart')
    
    return render(request, 'store/checkout.html', {'order': order})


@login_required
def complete_order(request):
    """
    Completes an order.
    Reduce stock from each product, and resets the shopping cart for the next purchases
    """
    order = get_object_or_404(Order, user=request.user, complete=False)

    for item in order.items.all():
        product = item.product
        if product and product.stock >= item.quantity:
            product.stock -= item.quantity
            product.save()

    order.complete = True
    order.save()
    
    return render(request, 'store/order_complete.html', {'order': order})