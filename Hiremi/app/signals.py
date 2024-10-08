from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Register, VerificationDetails


@receiver(post_save, sender=VerificationDetails)
def update_register(sender, instance, **kwargs):
    register = instance.register
    register.payment_status = instance.payment_status
    register.save()