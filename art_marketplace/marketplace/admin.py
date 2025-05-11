from django.contrib import admin
from .models import Artwork, UserProfile, Cart, Order, Notification, WithdrawalRequest

admin.site.register(Artwork)
admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(Order)

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'created_at', 'is_approved', 'is_rejected', 'comment')
    list_filter = ('is_approved', 'is_rejected', 'created_at')
    search_fields = ('user__username',)
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for obj in queryset:
            if not obj.is_approved and not obj.is_rejected:
                obj.is_approved = True
                obj.save()
                # Списываем средства с баланса
                profile = UserProfile.objects.get(user=obj.user)
                profile.balance = profile.balance - obj.amount
                profile.save()
        self.message_user(request, "Selected requests approved and balance updated.")
    approve_requests.short_description = "Approve selected withdrawal requests"

    def reject_requests(self, request, queryset):
        for obj in queryset:
            if not obj.is_approved and not obj.is_rejected:
                obj.is_rejected = True
                obj.save()
        self.message_user(request, "Selected requests rejected.")
    reject_requests.short_description = "Reject selected withdrawal requests" 