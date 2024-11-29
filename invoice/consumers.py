from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from inventory.models import Product
import json, asyncio

class InvoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data['action']

            if action == 'query_product':
                await self.filter_product(data)
            else:
                await self.send(text_data=json.dumps({'error': 'Acción no reconocida.'}))
        except json.JSONDecodeError as e:
            await self.send(text_data=json.dumps({
                'error': 'Error al decodificar JSON.',
                "message": str(e)
            }))
