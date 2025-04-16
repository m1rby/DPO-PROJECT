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

def get_template_name(template_name, request):
    """Возвращает имя шаблона с учетом языка"""
    if request.LANGUAGE_CODE == 'ru':
        return template_name.replace('.html', '_ru.html')
    return template_name

def get_message(message_key, request):
    """Возвращает сообщение на нужном языке"""
    messages = {
        'artwork_created': {
            'en': 'Artwork created successfully!',
            'ru': 'Произведение успешно добавлено!'
        },
        'artwork_added_to_cart': {
            'en': 'Artwork added to cart!',
            'ru': 'Произведение добавлено в корзину!'
        },
        'order_placed': {
            'en': 'Order placed successfully!',
            'ru': 'Заказ успешно оформлен!'
        },
        'profile_updated': {
            'en': 'Profile updated successfully!',
            'ru': 'Профиль успешно обновлен!'
        }
    }
    return messages[message_key][request.LANGUAGE_CODE]

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
    
    return render(request, get_template_name('marketplace/home.html', request), {
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
            messages.success(request, get_message('artwork_created', request))
            return redirect('artwork_detail', pk=artwork.pk)
    else:
        form = ArtworkForm()
    return render(request, get_template_name('marketplace/create_artwork.html', request), {'form': form})

@login_required
@require_POST
def toggle_like(request, artwork_id):
    print(f"Toggle like request received for artwork {artwork_id} from user {request.user.username}")
    artwork = get_object_or_404(Artwork, id=artwork_id)
    is_liked = artwork.toggle_like(request.user)
    print(f"Like status: {is_liked}, Likes count: {artwork.get_likes_count()}")
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
    
    return render(request, get_template_name('marketplace/artwork_detail.html', request), {
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
    messages.success(request, get_message('artwork_added_to_cart', request))
    return redirect('cart')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.artwork.price * item.quantity for item in cart_items)
    return render(request, get_template_name('marketplace/cart.html', request), {
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
        
        messages.success(request, get_message('order_placed', request))
        return redirect('orders')
    
    return render(request, get_template_name('marketplace/checkout.html', request), {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, get_template_name('marketplace/orders.html', request), {'orders': orders})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, get_message('profile_updated', request))
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    artworks = Artwork.objects.filter(artist=request.user)
    return render(request, get_template_name('marketplace/profile.html', request), {
        'form': form,
        'profile': profile,
        'artworks': artworks
    }) 