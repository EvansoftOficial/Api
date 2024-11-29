# Si eliminas el grupo, puedes ajustar el Signal para que no intente enviar a un grupo:
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from company.models import Resolution
from channels.layers import get_channel_layer

@receiver(post_save, sender=Resolution)
def notify_invoice_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        # Aquí puedes definir otro método para enviar el mensaje directamente si es necesario
        async_to_sync(channel_layer.send)(
            "specific_channel_name",  # Usa un nombre de canal específico si puedes asignarlo
            {
                "type": "invoice_update",
                "message": {
                    "_from": instance._from,
                    "prefix": instance.prefix,
                    "days_expiration": instance.generated_to_date
                }
            }
        )