from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

class Artwork(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artworks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='artworks/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_sold = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    materials = models.CharField(max_length=200, blank=True)
    views = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views += 1
        self.save()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s cart - {self.artwork.title}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='completed')

    def __str__(self):
        return f"Order #{self.id} - {self.artwork.title}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('artwork_approved', 'Artwork Approved'),
        ('artwork_sold', 'Artwork Sold'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"

class WithdrawalRequest(models.Model):
    METHOD_CHOICES = (
        ('card', 'Card'),
        ('paypal', 'PayPal'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    payment_details = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Withdrawal {self.amount} by {self.user.username} ({'Approved' if self.is_approved else 'Pending'})" 