from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import WithdrawalRequest, UserProfile

@receiver(pre_save, sender=WithdrawalRequest)
def handle_withdrawal_approval(sender, instance, **kwargs):
    if not instance.pk:
        return  # Новая заявка, не обрабатываем

    old = WithdrawalRequest.objects.get(pk=instance.pk)
    # Списываем только если статус изменился с не-одобрен на одобрен
    if not old.is_approved and instance.is_approved and not instance.is_rejected:
        profile = UserProfile.objects.get(user=instance.user)
        if profile.balance >= instance.amount:
            profile.balance -= instance.amount
            profile.save() 