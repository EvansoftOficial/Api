# invoice/routing.py
from django.urls import re_path
from . import consumers  # Importa tu consumidor

websocket_urlpatterns = [
    re_path(r'ws/invoice/$', consumers.InvoiceConsumer.as_asgi()),
]
