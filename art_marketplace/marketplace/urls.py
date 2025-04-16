from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artwork/<int:artwork_id>/toggle-like/', views.toggle_like, name='toggle_like'),
    path('create/', views.create_artwork, name='create_artwork'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:artwork_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('profile/', views.profile, name='profile'),
] 