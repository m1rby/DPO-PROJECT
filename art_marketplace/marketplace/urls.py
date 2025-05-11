from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('create/', views.create_artwork, name='create_artwork'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:artwork_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('profile/', views.profile, name='profile'),
    path('artwork/<int:artwork_id>/delete/', views.delete_artwork, name='delete_artwork'),
    path('accounts/signup/', views.signup, name='account_signup'),
    path('accounts/login/', views.login_view, name='account_login'),
] 