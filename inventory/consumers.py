from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Product
from company.models import Resolution
from invoice.models import Invoice
import json

class InventarioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data['action']

            if action == 'create':
                print("Estamos creando")
                await self.process_products(data)
            elif action == 'fetch_range':
                page = data.get('page', 1)
                per_page = data.get('page_size', 50)
                print(data)
                pk_branch = 71#data['pk_branch']
                result = await Product.get_paginated_products(page, per_page, pk_branch)
                await self.send(text_data=json.dumps(result))
            elif action == 'query_product':
                result = await Product.filter_product(data)
                await self.send(text_data=json.dumps(result))
            elif action == 'product_selected':
                result = await Product.get_product_by_code(data['pk'])
                await self.send(text_data=json.dumps(result))
            elif action == 'get_number':
                result = await Resolution.get_resolution(data)
                await self.send(text_data=json.dumps({"number": result}))
            elif action == 'create_invoice':
                value = json.loads(data['headers'])
                value['details'] = json.loads(data['details_invoice'])
                paymentform = paymentform = {
                    "paymentform": 1,
                    "paymentmethod": 10,
                    "due_date": value['date']
                }
                if int(value['paymentform']) == 2:
                    paymentform = {
                        "paymentform": 2,
                        "paymentmethod": 30,
                        "due_date": value['date_invoice_due']
                    }
                value['payment_form'] = paymentform
                print(value)
                result = await Invoice.create_invoice(value)
                await self.send(text_data=json.dumps(result))
            else:
                await self.send(text_data=json.dumps({'error': 'Acción no reconocida.'}))
        except json.JSONDecodeError as e:
            await self.send(text_data=json.dumps({
                'error': 'Error al decodificar JSON.',
                "message": str(e)
            }))

    async def process_products(self, products):
        result = await Product.create_multiple(products)
        await self.send(text_data=json.dumps(result))