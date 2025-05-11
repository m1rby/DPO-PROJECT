from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from .models import Artwork, UserProfile, Cart, Order, Notification, WithdrawalRequest
from .forms import ArtworkForm, UserProfileForm, ArtworkSearchForm, WithdrawalRequestForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import requests
from django.conf import settings
from django.utils import translation

def get_template_name(template_name, request):
    return template_name

def get_message(message_key, request=None):
    messages = {
        'artwork_created': 'Artwork created successfully!',
        'artwork_added_to_cart': 'Artwork added to cart!',
        'order_placed': 'Order placed successfully!',
        'profile_updated': 'Profile updated successfully!',
    }
    return messages[message_key]

def home(request):
    artworks = Artwork.objects.filter(is_sold=False, is_approved=True)
    search_form = ArtworkSearchForm(request.GET)
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        
        if query is not None and query != '':
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
    
    artworks = artworks.order_by('-created_at')[:12]
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
            messages.success(request, 'Your artwork has been submitted and will be published after admin approval.')
            return redirect('profile')
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
    
    return render(request, get_template_name('marketplace/artwork_detail.html', request), {
        'artwork': artwork
    })

@login_required
def add_to_cart(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id)
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
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        total_amount = 0
        
        for cart_item in cart_items:
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                artwork=cart_item.artwork,
                quantity=cart_item.quantity,
                total_price=cart_item.artwork.price * cart_item.quantity,
                status='completed'  # Явно указываем статус completed
            )
            
            # Обновляем баланс художника
            artist_profile = UserProfile.objects.get(user=cart_item.artwork.artist)
            artist_profile.balance += cart_item.artwork.price * cart_item.quantity
            artist_profile.save()
            
            # Обновляем статус картины
            cart_item.artwork.is_sold = True
            cart_item.artwork.save()
            
            # Создаем уведомление для художника
            create_notification(
                cart_item.artwork.artist,
                'artwork_sold',
                cart_item.artwork,
                f'Your artwork "{cart_item.artwork.title}" has been sold for ${cart_item.artwork.price}!'
            )
            
            total_amount += cart_item.artwork.price * cart_item.quantity
            
            # Удаляем товар из корзины
            cart_item.delete()
        
        messages.success(request, f'Your order has been placed successfully! Total amount: ${total_amount}')
        return redirect('orders')
    
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.artwork.price * item.quantity for item in cart_items)
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
    # Статистика
    artworks = Artwork.objects.filter(artist=request.user)
    artworks_sold = artworks.filter(is_sold=True).count()
    active_listings = artworks.filter(is_sold=False, is_approved=True).count()
    
    # Обновляем подсчет общей суммы продаж
    total_sales = Order.objects.filter(
        artwork__artist=request.user,
        status='completed'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Обработка формы редактирования профиля и вывода средств
    if request.method == 'POST':
        if 'phone' in request.POST:  # Это форма редактирования профиля
            profile.phone = request.POST.get('phone', '')
            profile.location = request.POST.get('location', '')
            profile.website = request.POST.get('website', '')
            profile.instagram = request.POST.get('instagram', '')
            profile.facebook = request.POST.get('facebook', '')
            profile.twitter = request.POST.get('twitter', '')
            profile.bio = request.POST.get('bio', '')
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:  # Это форма вывода средств
            amount = request.POST.get('amount')
            method = request.POST.get('method')
            payment_details = request.POST.get('payment_details')
            if amount and method and payment_details:
                try:
                    amount = float(amount)
                    if amount <= profile.balance:
                        WithdrawalRequest.objects.create(
                            user=request.user,
                            amount=amount,
                            method=method,
                            payment_details=payment_details
                        )
                        messages.success(request, 'Withdrawal request sent for moderation.')
                    else:
                        messages.error(request, 'Insufficient balance.')
                except ValueError:
                    messages.error(request, 'Invalid amount.')
            else:
                messages.error(request, 'Please fill in all fields.')
            return redirect('profile')  # <-- ВАЖНО: всегда редирект после POST!

    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, get_template_name('marketplace/profile.html', request), {
        'profile': profile,
        'artworks': artworks,
        'artworks_sold': artworks_sold,
        'active_listings': active_listings,
        'total_sales': total_sales,
        'withdrawals': withdrawals,
    })

@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    return render(request, 'marketplace/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

def create_notification(user, notification_type, artwork=None, message=None):
    if message is None:
        if notification_type == 'artwork_approved':
            message = f'Your artwork "{artwork.title}" has been approved and is now visible on the marketplace!'
        elif notification_type == 'artwork_sold':
            message = f'Your artwork "{artwork.title}" has been sold!'
    
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        artwork=artwork,
        message=message
    )

def approve_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    artwork.is_approved = True
    artwork.save()
    create_notification(artwork.artist, 'artwork_approved', artwork)
    return redirect('admin:marketplace_artwork_changelist')

@login_required
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    
    # Проверяем, является ли пользователь владельцем работы
    if artwork.artist != request.user:
        messages.error(request, 'You do not have permission to delete this artwork.')
        return redirect('profile')
    
    # Проверяем, не продана ли работа
    if artwork.is_sold:
        messages.error(request, 'Cannot delete sold artwork.')
        return redirect('profile')
    
    # Удаляем работу
    artwork.delete()
    messages.success(request, 'Artwork has been successfully deleted.')
    return redirect('profile')

def signup(request):
    with translation.override('en'):
        from allauth.account.views import SignupView
        class CustomSignupView(SignupView):
            template_name = 'account/signup.html'
            def form_valid(self, form):
                recaptcha_response = self.request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.RECAPTCHA_PRIVATE_KEY,
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                if not result.get('success'):
                    return self.render_to_response(self.get_context_data(form=form, recaptcha_error='Invalid reCAPTCHA. Please try again.'))
                return super().form_valid(form)
        return CustomSignupView.as_view()(request)

def login_view(request):
    with translation.override('en'):
        from allauth.account.views import LoginView
        class CustomLoginView(LoginView):
            template_name = 'account/login.html'
            def form_valid(self, form):
                recaptcha_response = self.request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.RECAPTCHA_PRIVATE_KEY,
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                if not result.get('success'):
                    return self.render_to_response(self.get_context_data(form=form, recaptcha_error='Invalid reCAPTCHA. Please try again.'))
                return super().form_valid(form)
        return CustomLoginView.as_view()(request) 