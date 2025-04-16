from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Artwork, UserProfile, Cart, Order
from .forms import ArtworkForm, UserProfileForm, ArtworkSearchForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def home(request):
    artworks = Artwork.objects.filter(is_sold=False).order_by('-created_at')[:12]
    search_form = ArtworkSearchForm(request.GET)
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        
        if query:
            artworks = artworks.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )
        if category:
            artworks = artworks.filter(category__icontains=category)
        if min_price:
            artworks = artworks.filter(price__gte=min_price)
        if max_price:
            artworks = artworks.filter(price__lte=max_price)
    
    return render(request, 'marketplace/home.html', {
        'artworks': artworks,
        'search_form': search_form
    })

@login_required
def create_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user
            artwork.save()
            messages.success(request, 'Artwork created successfully!')
            return redirect('artwork_detail', pk=artwork.pk)
    else:
        form = ArtworkForm()
    return render(request, 'marketplace/create_artwork.html', {'form': form})

@login_required
@require_POST
def toggle_like(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    is_liked = artwork.toggle_like(request.user)
    return JsonResponse({
        'is_liked': is_liked,
        'likes_count': artwork.get_likes_count()
    })

def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    artwork.increment_views()  # Increment views when artwork is viewed
    is_liked = False
    if request.user.is_authenticated:
        is_liked = request.user in artwork.likes.all()
    
    return render(request, 'marketplace/artwork_detail.html', {
        'artwork': artwork,
        'is_liked': is_liked
    })

@login_required
def add_to_cart(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        artwork=artwork,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, 'Artwork added to cart!')
    return redirect('cart')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.artwork.price * item.quantity for item in cart_items)
    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.artwork.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                artwork=item.artwork,
                quantity=item.quantity,
                total_price=item.artwork.price * item.quantity
            )
            item.artwork.is_sold = True
            item.artwork.save()
            item.delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('orders')
    
    return render(request, 'marketplace/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/orders.html', {'orders': orders})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    artworks = Artwork.objects.filter(artist=request.user)
    return render(request, 'marketplace/profile.html', {
        'form': form,
        'profile': profile,
        'artworks': artworks
    }) 