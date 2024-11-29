from from_number_to_letters import Thousands_Separator
from company.models import Branch, License, Resolution
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime, timedelta
from django.db.models import Sum, F, Min, Max
from inventory.models import Product
from channels.db import database_sync_to_async
from django.core import serializers
from django.core.files import File
from django.utils import timezone
from user.models import Employee
from customer.models import *
from setting.models import *
from django.db import models
import json, qrcode, env
from io import BytesIO
from PIL import Image

class Cash_Closings(models.Model):
	totals_subtotal = models.FloatField(default = 0,null = True, blank = True)
	totals_taxes = models.FloatField(default = 0,null = True, blank = True)
	totals_ipo = models.FloatField(default = 0,null = True, blank = True)
	totals_discount = models.FloatField(default = 0,null = True, blank = True)
	totals = models.FloatField(default = 0,null = True, blank = True)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE,null = True, blank = True)
	time_start = models.TimeField(auto_now_add = True)
	time_end = models.TimeField(null=True, blank=True)
	base = models.FloatField(null = True, blank = True)
	finalized = models.BooleanField(default = False,null = True, blank = True)

	def __str__(self):
		return f"Cierre de Caja - {self.time_start} por {self.employee}"

	@classmethod
	def create_cash_closing(cls,data):
		result = False
		message = None
		try:
			active_closing = cls.objects.filter(finalized=False, employee = Employee.objects.get(pk = data['pk_employee'])).exists()
			if active_closing:
				message = "There is already an active cash closing. Cannot create a new one."
			else:
				cash_closing = cls(base = data['base'],employee = Employee.objects.get(pk = data['pk_employee']))
				cash_closing.save()
				result = True
				message = "Record created successfully"
		except ObjectDoesNotExist:
			message = "Employee not found."
		except Exception as e:
			message = str(e)
		with open("/deploy/api/errores/create_cash_closing.txt",'w') as f:
			f.write(str(message))
		return {'result':result, 'message':message}

	@classmethod
	def update_cash_clossing(cls, data,employee,payment_):
		result = False
		message = None
		try:
			cash_closing = cls.objects.get(employee = employee,finalized = False)
			cash_closing.totals_subtotal = (cash_closing.totals_subtotal or 0) + (float(data['price'] * data['quantity']))
			cash_closing.totals_taxes = (cash_closing.totals_taxes or 0) + (float(data['tax'] * data['quantity']))
			cash_closing.totals_ipo = (cash_closing.totals_ipo or 0) + (float(data['ipo'] * data['quantity']))
			cash_closing.totals_discount = (cash_closing.totals_discount or 0) + (float(data['discount'] * data['quantity']))
			cash_closing.totals = cash_closing.totals_subtotal + cash_closing.totals_taxes + cash_closing.totals_ipo + cash_closing.totals_discount
			cash_closing.save()
			total_amount = (float(data['price'] * data['quantity'])) + (float(data['tax'] * data['quantity'])) + (float(data['ipo'] * data['quantity'])) + (float(data['discount'] * data['quantity']))
			result = True
			message = "Success"
			cash_closing.add_payment_method(method_name=payment_, amount = total_amount)
		except ObjectDoesNotExist:
			message = "Employee not found."
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	def add_payment_method(self, method_name, amount):
		payment_method = PaymentMethod(cash_closing=self, method_name=method_name, amount=amount)
		payment_method.save()


	@classmethod
	def cash_closing(cls, data):
	    # Si no se pasa una fecha, se toma la del día actual
	    print(data)
	    date = data['date']
	    result = False
	    if not date:
	        date = timezone.now().date()

	    # Obtenemos el cierre de caja activo para el empleado
	    try:
	        active_cash_closing = Cash_Closings.objects.get(employee=data['pk_employee'], finalized=False)
	        print(active_cash_closing)
	    except Cash_Closings.DoesNotExist:
	    	print(data)
	    	employee = Employee.objects.get(pk = data['pk_employee'])
	    	return {
	    		"result": result,
			    "message": "No hay un cierre de caja activo para este empleado.",
			    "data": {
			        "branch_name": Branch.objects.get(pk = data['pk_branch']).name,
			        "numero_factura_inicial": 0,
			        "numero_factura_final": 0,
			        "total_ventas": 0,
			        "totals_invoice": 0,
			        "total_impuestos": 0,
			        "total_descuentos": 0,
			        "total_consumo": 0,
			        "total_cantidad": 0,
			        "pagos": [
			            {
			                "payment_method__name": "NO HAY REGISTRO",
			                "total": "0"
			            }
			        ],
			        "time_start": timezone.now().date(),
			        "time_end": timezone.now().date(),
			        "seller": f"{employee.first_name} {employee.surname}"
			    }
			}

	    # Filtramos las facturas del día para la sucursal seleccionada que no están anuladas ni canceladas
	    facturas = Invoice.objects.filter(
	        date=date,
	        branch_id=data['pk_branch'],
	        annulled=False,
	        cash_closing_invoice = active_cash_closing  # Filtrar por el cierre de caja activo
	    )

	    # Si no hay facturas, retornamos un mensaje
	    if not facturas.exists():
	    	active_cash_closing.time_end = timezone.now().time()
	    	active_cash_closing.finalized = True
	    	active_cash_closing.save()
	    	employee = Employee.objects.get(pk = data['pk_employee'])
	    	return {
	    		"result": result,
	            "message": "No hay facturas para el cierre de caja.",
	            "data": {
			        "branch_name": Branch.objects.get(pk = data['pk_branch']).name,
			        "numero_factura_inicial": 0,
			        "numero_factura_final": 0,
			        "total_ventas": 0,
			        "totals_invoice": 0,
			        "total_impuestos": 0,
			        "total_descuentos": 0,
			        "total_consumo": 0,
			        "total_cantidad": 0,
			        "pagos": [
			            {
			                "payment_method__name": "NO HAY REGISTRO",
			                "total": "0"
			            }
			        ],
			        "time_start": active_cash_closing.time_start.strftime("%H:%M"),
			        "time_end": active_cash_closing.time_end.strftime("%H:%M"),
			        "seller": f"{employee.first_name} {employee.surname}"
			    }
	        }

	    branch = facturas.first().branch  # Asumiendo que todas las facturas tienen la misma sucursal
	    branch_name = branch.name if branch else "Sucursal no encontrada"
	    numero_factura_inicial = facturas.aggregate(min_num=Min('number'))['min_num']
	    numero_factura_final = facturas.aggregate(max_num=Max('number'))['max_num']

	    # Sumamos los totales de las facturas y otros campos relevantes
	    total_ventas = facturas.aggregate(total=Sum(F('details_invoice__price') * F('details_invoice__quantity')))['total'] or 0
	    total_impuestos = facturas.aggregate(impuestos=Sum(F('details_invoice__tax') * F('details_invoice__quantity')))['impuestos'] or 0
	    total_descuentos = facturas.aggregate(descuentos=Sum('details_invoice__discount'))['descuentos'] or 0
	    total_consumo = facturas.aggregate(consumo=Sum('details_invoice__ipo'))['consumo'] or 0

	    totals_invoice = total_ventas + total_impuestos + total_consumo

	    # Sumamos las cantidades de productos vendidos
	    total_cantidad = Details_Invoice.objects.filter(invoice__in=facturas).aggregate(cantidad=Sum('quantity'))['cantidad'] or 0

	    # Sumamos los diferentes métodos de pago utilizados
	    pagos = Payment_Forms.objects.filter(invoice__in=facturas).values('payment_method__name').annotate(total=Sum('invoice__total'))
	    for pago in pagos:
	    	pago['total'] = Thousands_Separator(pago['total'])

	    active_cash_closing.time_end = timezone.now().time()
	    active_cash_closing.finalized = True
	    active_cash_closing.save()
	    result = True
	    # Preparar la respuesta
	    cierre_caja_resumen = {
	        "branch_name": branch_name,
	        "numero_factura_inicial": numero_factura_inicial,
	        "numero_factura_final": numero_factura_final,
	        "total_ventas": Thousands_Separator(total_ventas),
	        "totals_invoice": Thousands_Separator(totals_invoice),
	        "total_impuestos": Thousands_Separator(total_impuestos),
	        "total_descuentos": Thousands_Separator(total_descuentos),
	        "total_consumo": Thousands_Separator(total_consumo),
	        "total_cantidad": Thousands_Separator(total_cantidad),
	        "pagos": list(pagos),
	        "time_start": active_cash_closing.time_start.strftime("%H:%M"),
	        "time_end": active_cash_closing.time_end.strftime("%H:%M"),
	        "seller": f"{active_cash_closing.employee.first_name} {active_cash_closing.employee.surname}"
	    }

	    print(cierre_caja_resumen)
	    

	    return {
	    	"result": result,
	        "message": "Cierre de caja exitoso.",
	        "data": cierre_caja_resumen
	    }



class Invoice(models.Model):
	type_document = models.IntegerField()
	number = models.IntegerField()
	prefix = models.CharField(max_length = 7) 
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	date = models.CharField(max_length = 12) 
	time = models.TimeField(auto_now_add = True)
	total = models.FloatField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	cancelled = models.BooleanField(default = True)
	hidden = models.BooleanField(default = False)
	state = models.CharField(max_length = 70,null = True, blank = True)
	annulled = models.BooleanField(default = False)
	cufe = models.CharField(max_length = 100,null = True, blank = True)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)
	urlinvoicexml = models.CharField(max_length = 250, null = True, blank = True)
	urlinvoicepdf = models.CharField(max_length = 250, null = True, blank = True)
	attacheddocument = models.CharField(max_length = 250, null = True, blank = True)
	QRStr = models.CharField(max_length = 500, null = True, blank = True)
	cude = models.CharField(max_length = 100, null = True, blank = True)
	urlinvoicexml_nc = models.CharField(max_length = 250, null = True, blank = True)
	urlinvoicepdf_nc = models.CharField(max_length = 250, null = True, blank = True)
	attacheddocument_nc = models.CharField(max_length = 250, null = True, blank = True)
	QRStr_nc = models.CharField(max_length = 500, null = True, blank = True)
	consumption_tax = models.BooleanField(default = False)
	discount = models.FloatField(default = 0)
	cash_closing_invoice = models.ForeignKey(Cash_Closings, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name}"

	@staticmethod
	def generate_qr_code(data,name_qr):
		result = False
		message = None
		try:
			qr = qrcode.QRCode(
			    version=1,
			    error_correction=qrcode.constants.ERROR_CORRECT_L,
			    box_size=10,
			    border=4,
			)
			qr.add_data(data)
			qr.make(fit=True)
			img = qr.make_image(fill_color="rgb(0, 0, 255)", back_color="rgb(255, 255, 255)")
			img = img.convert("RGBA")
			buffer = BytesIO()
			img.save(f"{env.URL_QR_IN_USE}{name_qr}.png")
		except Exception as e:
			message = str(e)
		return buffer

	@classmethod
	def generate_qr_code_view(cls, data):
		invoice = Invoice.get_invoice(data['pk_invoice'])
		name_qr = f"{invoice['prefix']}{invoice['number']}"
		time = datetime.strptime(invoice['time'], "%H:%M:%S.%f")
		invoice_data = f"""Factura: {invoice['prefix']}{invoice['number']}\nEstablecimiento: {invoice['branch']['name']}\nFecha: {invoice['date']}\nHora: {time.strftime("%H:%M:%S")}\nTotal de la factura{invoice['total']}\nNombre del Cliente: {invoice['customer']['name']}"""
		qr_code_buffer = cls.generate_qr_code(invoice_data, name_qr)
		return True

	@classmethod
	def send_invoice_dian(cls, data):
		result = False
		message = None
		_data = None
		try:
			invoice = Invoice.get_invoice(data['pk_invoice'])
			if invoice is not None:
				_data = Send_Dian(invoice).Send(data['type_document'], Invoice.objects.get(pk = data['pk_invoice']))
				message = "Success"
				result = True
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message, 'data': _data}

	@classmethod
	def get_selling_by_invoice(cls, data):
	    filtered_invoices = cls.objects.filter(
	        type_document=data['type_document'], 
	        branch=Branch.objects.get(pk=data['pk_branch']), 
	        date=date.today()
	    )
	    
	    total = sum(
	        int(json.loads(serializers.serialize('json', [i]))[0]['fields']['total'])
	        for i in filtered_invoices
	    )
	    
	    annulled = [
	        json.loads(serializers.serialize('json', [i]))[0]['fields']['annulled']
	        for i in filtered_invoices
	    ]
	    
	    return {
	        'total': total,
	        'annulled': annulled
	    }


	@classmethod
	def get_selling_by_date(cls, data):
	    branch = Branch.objects.get(pk=data['pk_branch'])
	    start_date = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
	    end_date = date.today() + timedelta(days=1)
	    totals_by_date = {str(start_date + timedelta(days=i)): 0 for i in range((end_date - start_date).days)}
	    invoice = cls.objects.filter(branch=branch, date__range=(start_date, end_date), annulled = False)
	    for i in invoice:
	    	print(i.total)
	    	invoice_date = str(i.date)
	    	total = int(i.total) if i.total is not None else 0
	    	totals_by_date[invoice_date] = totals_by_date.get(invoice_date, 0) + total
	    return totals_by_date

	@staticmethod
	def values_taxes(cls,invoice,tax):
		total_base = 0
		total_tax = 0
		for item in invoice:
		    if int(tax) == int(item['tax_value']) and int(tax) != 45:
		        total_tax += round((item['tax']  * item['quantity']))
		        total_base += round((item['cost'] ) * item['quantity'])
		    if int(item['ipo']) > 0 and int(tax) == 45:
		        total_tax += round((item['ipo']  * item['quantity']))
		        total_base +=  round((item['cost'] ) * item['quantity'])
		        cls.quantity_ipo = item['quantity']
		        cls.ipo_unit = item['ipo']
		return {str(tax): total_tax, 'base': total_base}

	@staticmethod
	def Tax_Totals(cls,invoice):
	    taxes = []
	    tax_19 = cls.values_taxes(cls,invoice, 19)
	    tax_5 = cls.values_taxes(cls,invoice, 5)
	    tax_0 = cls.values_taxes(cls,invoice, 0)
	    ipo_value = cls.values_taxes(cls,invoice, 45)

	    if tax_19['base'] != 0:
	        taxes.append({
	            "tax_id": 1,
	            "tax_amount": str(Thousands_Separator((round(tax_19['19'])))),
	            "percent": "19",
	            "taxable_amount": str(Thousands_Separator((round(tax_19['base'])))),
	            "name":'IVA'
	        })
	    if tax_5['base'] != 0:
	        taxes.append({
	            "tax_id": 1,
	            "tax_amount": str(tax_5['5']),
	            "percent": "5",
	            "taxable_amount": str(tax_5['base']),
	            "name":'IVA'
	        })
	    if tax_0['base'] != 0:
	        taxes.append({
	            "tax_id": 1,
	            "tax_amount": str(tax_0['0']),
	            "percent": "0",
	            "taxable_amount": str(tax_0['base']),
	            "name":'IVA'
	        })
	    if int(ipo_value['base']) != 0:
	        taxes.append(
	            {
	                "tax_id": 19,
	                "tax_amount": int(ipo_value['45']),
	                "percent": "0",
	                "taxable_amount": int(ipo_value['base']),
	                "unit_measure_id": "70",
	                "per_unit_amount": cls.quantity_ipo,
	                "base_unit_measure": cls.ipo_unit,
	                "name":'IPOC'
	            }
	        )
	    return taxes

	@classmethod
	def get_invoice(cls, pk):
		_invoice = cls.objects.get(pk = pk)
		serialized_invoice = serializers.serialize('json', [_invoice])
		invoice = json.loads(serialized_invoice)[0]
		data = invoice['fields']
		data['pk_invoice'] = pk
		list_details = []
		for i in Details_Invoice.objects.filter(invoice = _invoice):
			serialized_invoice = serializers.serialize('json', [i])
			product = json.loads(serialized_invoice)[0]['fields']
			product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
			list_details.append(product)
		data['details'] = list_details
		serialized_paymentform = serializers.serialize('json', [Payment_Forms.objects.get(invoice = _invoice)])
		data['payment_form'] = json.loads(serialized_paymentform)[0]['fields']
		data['company'] = json.loads(serializers.serialize('json', [_invoice.branch.company]))[0]['fields']
		data['company']['logo_url'] = f"{env.URL_LOCAL}/media/{data['company']['logo']}"
		data['metod'] = "Crédito" if data['payment_form'] == 2 else "Efectivo"
		serialized_customer = serializers.serialize('json', [Customer.objects.get(pk = _invoice.customer.pk)])
		data['customer'] = json.loads(serialized_customer)[0]['fields']
		_branch = Branch.objects.get(pk = _invoice.branch.pk)
		branch = serializers.serialize('json', [_branch])
		data['branch'] = json.loads(branch)[0]['fields']
		resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = data['type_document'])])
		data['resolution'] = json.loads(resolution)[0]['fields']
		data['resolution']['to'] = data['resolution']['_to']
		data['type_document_id_company'] = Type_Document_I.objects.get(pk = data['company']['type_regime']).name
		data['branch']['municipalities_branch'] = Municipalities.objects.get(pk = data['branch']['municipality']).name
		data['payment_form']['name_payment_method'] = Payment_Method.objects.get(pk = data['payment_form']['payment_method']).name
		data['list_taxes'] = cls.Tax_Totals(cls,data['details'])
		print(data)

		return data

	@classmethod
	def annulled_invoice(cls, data):
		result = False
		message = None
		try:
			invoice = Invoice.get_invoice(data['pk_invoice'])
			_data = Send_Dian(invoice).Send(4, Invoice.objects.get(pk = data['pk_invoice']))
			# if _data['result']:
			invoice = cls.objects.get(pk = data['pk_invoice'], annulled = False)
			branch = invoice.branch
			invoice.annulled = True
			invoice.state = "Factura Anulada."
			invoice.save()
			for i in Details_Invoice.objects.filter(invoice = invoice):
				product = Product.objects.get(code = i.code)
				product.quantity += i.quantity
				product.save()
			result = True
			message = "Success"
			employee = Employee.objects.get(pk = data['pk_employee'])
			serialized_employee = serializers.serialize('json', [employee])
			employee = json.loads(serialized_employee)[0]['fields']
			serialized_invoice = serializers.serialize('json', [invoice])
			invoice = json.loads(serialized_invoice)[0]['fields']
			History_Invoice.create_history_invoice(invoice, employee, 'Annulled', branch)
		except Exception as e:
			message = str(e)
			print(e)
		return {'result':result, 'message':message}


	@classmethod
	def annulled_invoice_by_product(cls, data):
	    result = False
	    message = None
	    try:
	        invoice = cls.objects.get(pk=data['pk_invoice'], annulled=False)
	        for detail_invoice in Details_Invoice.objects.filter(invoice=invoice):
	            product = Product.objects.get(code=data['code'])
	            quantity = int(data['quantity'])
	            if detail_invoice.quantity >= quantity:
		            if detail_invoice.quantity > 0:
		                product.quantity += quantity
		                total = round((detail_invoice.cost + detail_invoice.tax + detail_invoice.ipo) * (detail_invoice.quantity - quantity))
		                detail_invoice.price = total
		                detail_invoice.quantity -= quantity
		                product.save()
		                detail_invoice.save()
		                invoice.total = total
		                data_invoice = Invoice.get_invoice(data['pk_invoice'])
		                result_credit_note = Credi_Note_Product(
		                	data_invoice,
		                	data['code'], data['quantity'], 1, "Devolucion de producto",
		                	Resolution.get_number(9)
		                ).Send()
		                invoice.cude = result_credit_note['cude']
		                total_ncp = round((detail_invoice.cost + detail_invoice.tax) * quantity)
		                quantity_send = Note_Credit_Product.create_nc_by_product(detail_invoice, quantity, total_ncp, invoice)
		                invoice.note += f"Se aplico nota credito al producto {product.name} - Codigo {product.code} | Quitando {data['quantity']} productos\n"
		                invoice.save()
		                if detail_invoice.quantity <= 0:
		                	invoice.annulled = True
		                	invoice.save()
		                	message = "The product is already at zero"
		                result = True
		                message = "Success"
		            else:
		            	invoice.annulled = True
		            	invoice.save()
		            	message = "The product is already at zero"
	    except cls.DoesNotExist:
	        message = "Invoice does not exist"
	    except Details_Invoice.DoesNotExist:
	        message = "Invoice details do not exist"
	    except Product.DoesNotExist:
	        message = "Product does not exist"
	    except Exception as e:
	        message = str(e)
	    return {'result': result, 'message': message}

	@classmethod
	def get_list_invoice(cls, data):
		branch = Employee.objects.get(pk = data['pk_employee']).branch
		result = False
		message = None
		_data = None
		try:
			_data = [
				{
					"type_document":i.type_document,
					'pk_invoice': i.pk,
					'number': i.number,
					'prefix': i.prefix,
					'date': i.date,
					'name_client': i.customer.name,
					'total': i.total,
					"state":i.state,
					"cancelled":i.cancelled,
					"annulled":i.annulled,
					"cufe": i.cufe,
					"pdf": i.urlinvoicepdf,
					"pk_company": branch.company.documentI
				}
				for i in cls.objects.filter(branch = branch).order_by('-pk')
			]
		except Exception as e:
			print(e)
			message = str(e)
			_data = []
		return _data

	@classmethod
	@database_sync_to_async
	def create_invoice(cls, data):
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		total = 0
		pk_invoice = None
		customer = Customer.objects.get(pk = data['pk_customer'])
		branch = employee.branch
		invoice = None
		type_document = 1
		try:			
			validate = License.validate_date(employee.branch)
			if validate['result']:
				license = License.discount_license(employee.branch)
				if license['result']:
					cc = None
					try:
						cc = Cash_Closings.objects.get(employee=employee, finalized=False)
					except Exception as ex_cc:
						cc = None
					resolution = Resolution.get_number(data['type_document'], branch)
					invoice = cls(
						type_document = data['type_document'],
						number = resolution._from,
						prefix = resolution.prefix,
						branch = employee.branch,
						date = data['date'],
						note = data['note'],
						customer = customer,
						hidden = True if data['type_document'] == 99 else False,
						state = data['state'],
						employee = employee,
						consumption_tax = True if data['consumption_tax'] else False,
						discount = 0,
						cash_closing_invoice = cc
					)
					type_document = data['type_document']
					invoice.save()
					pk_invoice = invoice.pk
					result = True
					message = "Fails"
					payment = Payment_Form.objects.get(_id = data['payment_form']['paymentform']).name
					if result:
						for i in data['details']:
							value = Details_Invoice.create_details(i,invoice,employee,payment,cc)
							if not value['result']:
								result = False
								message = value['message']
								break
							else:
								result = value['result']
								message = value['message']
								total += float(value['total'])
					if result:
						value = Payment_Forms.create_paymentform(data, invoice, employee)
						result = value['result']
						message = value['message']
						if result:
							total += (total * (branch.consumption_tax / 100)) if invoice.consumption_tax else 0
							invoice.total = total
							invoice.save()
							values_wallet = {"pk_customer":customer.pk, 'amount_invoice':total}
							# Wallet_Customer.update_coins(values_wallet)
							_data = {'type_document':data['type_document'], 'pk_branch':employee.branch.pk}
							Resolution.add_number(_data)
							serialized_employee = serializers.serialize('json', [employee])
							employee = json.loads(serialized_employee)[0]['fields']
							serialized_invoice = serializers.serialize('json', [invoice])
							invoice = json.loads(serialized_invoice)[0]['fields']
							History_Invoice.create_history_invoice(invoice, employee, 'Created',branch)
						else:
							invoice.delete()

					if result:
						_data_ = {'pk_invoice':pk_invoice,'type_document': type_document}
						Invoice.send_invoice_dian(_data_)
					from accounting.models import AccountingEntry as account
					data['pk_invoice'] = pk_invoice
					data['pk_branch'] = branch.pk
					account.generate_accounting(data)
				else:
					result = license['result']
					message = license['message']
			else:
				result = validate['result']
				message = validate['message']
		except Exception as e:
			message = str(e)
			print(e, 'Created Invoice')
			#invoice.delete()
		return {'result':result, 'message':message,'pk_invoice': pk_invoice}

	@classmethod
	def get_list_invoice_credit(cls, branch):
		return [
			{
				"pk_invoice" : i.pk,
				"number": i.number,
				"prefix": i.prefix,
				"date": i.date,
				"total": i.total,
				"pk_customer":i.customer.pk,	
				"name_customer":i.customer.name
			}
			for i in cls.objects.filter(branch = branch, cancelled = False).order_by('-date')
		]


	@classmethod
	def cash_closing(cls,data):
	    # Si no se pasa una fecha, se toma la del día actual
	    date = data['date'] 
	    if not date:
	        date = timezone.now().date()

	    # Filtramos las facturas del día para la sucursal seleccionada que no están anuladas ni canceladas
	    facturas = Invoice.objects.filter(
	        date=data['date'],
	        branch_id=data['pk_branch'],
	        annulled=False
	    )

	    # Si no hay facturas, retornamos un mensaje
	    if not facturas.exists():
	        return {
	            "message": "No hay facturas para el cierre de caja.",
	            "data": None
	        }

	    branch = facturas.first().branch  # Asumiendo que todas las facturas tienen la misma sucursal
	    branch_name = branch.name if branch else "Sucursal no encontrada"
	    numero_factura_inicial = facturas.aggregate(min_num=Min('number'))['min_num']
	    numero_factura_final = facturas.aggregate(max_num=Max('number'))['max_num']

	    # Sumamos los totales de las facturas y otros campos relevantes
	    total_ventas = facturas.aggregate(total=Sum(F('details_invoice__price') * F('details_invoice__quantity')))['total'] or 0
	    totals_invoice = facturas.aggregate(total=Sum('total'))['total'] or 0
	    total_impuestos = facturas.aggregate(impuestos=Sum(F('details_invoice__tax')  * F('details_invoice__quantity')))['impuestos'] or 0
	    total_descuentos = facturas.aggregate(descuentos=Sum('details_invoice__discount'))['descuentos'] or 0
	    total_consumo = facturas.aggregate(consumo=Sum('consumption_tax'))['consumo'] or 0

	    # Sumamos las cantidades de productos vendidos
	    total_cantidad = Details_Invoice.objects.filter(invoice__in=facturas).aggregate(cantidad=Sum('quantity'))['cantidad'] or 0

	    # Sumamos los diferentes métodos de pago utilizados
	    pagos = Payment_Forms.objects.filter(invoice__in=facturas).values('payment_method__name').annotate(total=Sum('invoice__total'))

	    # Retornamos el resumen del cierre de caja
	    cierre = {
	        "total_ventas": Thousands_Separator(total_ventas),
	        "total_impuestos": Thousands_Separator(total_impuestos),
	        "total_descuentos": Thousands_Separator(total_descuentos),
	        "total_cantidad_productos": Thousands_Separator(total_cantidad),
	        "total_consumo": Thousands_Separator(total_consumo),
	        "detalle_pagos": list(pagos),
	        "numero_factura_inicial": numero_factura_inicial,
        	"numero_factura_final": numero_factura_final,
        	"branch_name": branch_name,
        	"total_factura":Thousands_Separator(totals_invoice),

	    }

	    return {
	        "message": "Cierre de caja generado exitosamente.",
	        "data": cierre
	    }


class Details_Invoice(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	ultra_processed = models.FloatField(default = 0)
	discount = models.FloatField()
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	unit_measures = models.CharField(max_length = 191, null=True, blank = True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)
	value_increase = models.FloatField(default = 0, null=True, blank = True)
	identification = models.IntegerField(default = 0, null=True, blank = True)

	def __str__(self):
		return f"{self.code} - {self.name} - {self.quantity}"

	@classmethod
	def create_details(cls, data, invoice,employee,payment,cc):
		result = False
		message = None
		cost = 0
		try:
			product = Product.objects.get(pk = data['pk_product'])
			ultra_processed = product.ultra_processed
			cost = round( (int(data['price']) + int(data['tax'])))
			details_invoice = cls(
				identification = product.pk,
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data['price'],
				price = data['price'],
				ipo = data['ipo'],
				ultra_processed = ultra_processed,
				discount = data['discount'],
				unit_measures = product.unit_measures.name,
				invoice = invoice,
				tax_value = product.tax,
				value_increase = data['value_increase']
			)
			details_invoice.save()
			result = True
			message = "Success"
			json = False
			if 'postman' in data:
				json = True
			if result:
				if invoice.type_document != 16:
					value = Product.discount_product(data['pk_product'], invoice.branch, int(data['quantity']), invoice.employee, json)
					if cc is not None:
						Cash_Closings.update_cash_clossing(data,employee,payment)
					if not value['result']:
						result = value['result']
						message = value['message']
						invoice.delete()
						return {'result':result, 'message':message,'total':data['totalValue']}
		except Exception as e:
			message = str(e)

		return {'result':result, 'message':message,'total':data['totalValue']}

class Payment_Forms(models.Model):
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 12)
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, invoice, employee):
		result = False
		message = None
		try:
			payment_form = cls(
				payment_form = Payment_Form.objects.get(_id = data['payment_form']['paymentform']),
				payment_method = Payment_Method.objects.get(_id = data['payment_form']['paymentmethod']),
				payment_due_date = data['payment_form']['due_date'],
				invoice = invoice
			)
			branch = employee.branch
			payment_form.save()
			if data['payment_form']['paymentform'] == 2:
				invoice.cancelled = False
				invoice.save()
				_data = {
					"pk_invoice": invoice.pk,
					"amount":0,
					"note":"There are no pass yet",
					"pk_employee": employee.pk
				}
				Pass.create_pass(_data)
				result = True
				message = "Success"
			else:
				employee = Employee.objects.get(pk = employee.pk)
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Created', branch)
				result = value['result']
				message = value['message']
		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}



class Pass(models.Model):
	number_pass = models.IntegerField()
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	amount = models.FloatField()
	date = models.DateTimeField(auto_now_add = True)
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)


	@classmethod
	def create_pass(cls, data):
		try:
			number = len(cls.objects.all())
		except Exception as e:
			pass
		invoice = Invoice.objects.get(pk = data['pk_invoice'])
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		try:
			_pass = cls.objects.get(invoice = invoice)
			if _pass.amount < invoice.total:
				if float(data['amount']) <= (invoice.total - _pass.amount) and float(data['amount']) > 0:
					_pass.amount += float(data['amount'])
					message = "Credit to the invoice was accepted"
					result = True
				else:
					message = "You cannot pay more than the total invoice"
		except cls.DoesNotExist as e:
			_pass = cls(
				number_pass = number if number > 0 else 1,
				invoice = invoice,
				amount = data['amount'],
				note = data['note']
			)
			message = f"Credit to the invoice {invoice.number} was created successfully"
			result = True
		_pass.save()
		if _pass.amount == invoice.total:
			invoice.cancelled = True
			invoice.save()
			message = "The invoice has already been canceled"

		serialized_invoice = serializers.serialize('json', [invoice])
		serialized_customer = serializers.serialize('json', [invoice.customer])

		customer = json.loads(serialized_customer)[0]['fields']
		invoice = json.loads(serialized_invoice)[0]['fields']

		employee = serializers.serialize('json', [employee])

		if result:
			History_Pass.create_history_pass(invoice, data['amount'], customer, data['note'], employee, branch)
		return {'result':True, 'message':message}

	@classmethod
	def cancel_all_invoices(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		customer = Customer.objects.get(pk = data['pk_customer'])
		pk = customer.pk
		invoice = Invoice.objects.filter(branch= employee.branch, cancelled = False, customer = customer)
		total = 0
		result = False
		message = None
		amount = data['amount']
		branch = employee.branch
		for i in invoice:
			total += i.total

		if total == amount:
			for i in invoice:
				_pass = cls.objects.get(invoice = i)
				_pass.amount = i.total
				_pass.save()
				i.cancelled = True
				i.save()
				result = True
				message = "Invoice paid"
		else:
			note = None
			for i in invoice:
				if amount >= i.total:
					_pass = cls.objects.get(invoice = i)
					_pass.amount = i.total
					amount -= i.total
					i.cancelled = True
					_pass.save()
					note = "Pago factura"
					serialized_invoice = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_invoice = json.loads(serialized_invoice)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_invoice, data['amount'], customer, note , __employee,branch)
				else:
					_pass = cls.objects.get(invoice = i)
					_pass.amount += amount
					_pass.save()
					note = "Abona a la factura"
					serialized_invoice = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_invoice = json.loads(serialized_invoice)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_invoice, data['amount'], customer, note , __employee,branch)
					if not _pass.invoice.cancelled:
						amount -= _pass.amount
						if amount <= 0:
							break
				i.save()
				result = True
				message = "Invoice paid"
		values = {"pk_customer": pk, "amount": amount}
		Wallet_Customer.update_wallet_customer(data)
		return {'result':result, 'message':message,"returned_value":amount}

class History_Invoice(models.Model):
	ACTION_CHOICES = (
	    ('Created', 'Created'),
	    ('Modified', 'Modified'),
	    ('Deleted', 'Deleted'),
	    ('Annulled', 'Annulled'),
	)
	action = models.CharField(max_length=10, choices=ACTION_CHOICES,null = True, blank = True)
	invoice = models.JSONField()
	employee = models.JSONField()
	date_registration = models.DateTimeField(auto_now_add = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE,null = True, blank = True)

	@classmethod
	def create_history_invoice(cls, invoice, employee, action,branch):
		result = False
		message = None
		try:
			hi = cls(
				invoice = invoice,
				employee = employee,
				action = action,
				branch = branch
			)
			hi.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

class History_Pass(models.Model):
	invoice = models.JSONField(null = True, blank = True)
	amount = models.FloatField(null = True, blank = True)
	customer = models.JSONField(null = True, blank = True)
	employee = models.JSONField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	date_registration = models.DateTimeField(auto_now_add = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE,null = True, blank = True)

	@classmethod
	def create_history_pass(cls, invoice, amount, customer, note, employee, branch):
		result = False
		message = None
		try:
			hp = cls(
				invoice = invoice,
				amount = amount,
				customer = customer,
				note = note,
				employee = employee,
				branch = branch
			)
			hp.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

class Note_Credit_Product(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
	quantity_send = models.IntegerField(default = 0, null = True, blank = True)

	@classmethod
	def create_nc_by_product(cls, product, quantity, total, invoice):
		result = False
		message = None
		quantity_send = 0
		try:
			ncp = cls.objects.get(invoice = invoice)
		except Exception as e:
			ncp = None
		if ncp is None:
			try:
				ncp = cls(
					code = product.code,
					name = product.name,
					quantity = quantity,
					tax = product.tax,
					cost = product.cost,
					price = total,
					ipo = product.ipo,
					discount = product.discount,
					invoice = invoice,
					employee = invoice.employee,
				)
				ncp.save()
				ncp.quantity_send += quantity
				ncp.save()
				quantity_send = ncp.quantity_send
				ncp.price = round((ncp.cost + ncp.tax) * ncp.quantity_send)
				ncp.save()
				result = True
				message = "Success"
			except Exception as e:
				message = f'{e} Product NC'
		else:
			ncp.quantity_send += quantity
			ncp.save()
			ncp.price = round((ncp.cost + ncp.tax) * ncp.quantity_send)
			ncp.save()
			quantity_send = ncp.quantity_send
			result = True
			message = "Success"
		return {'result':result, 'message':message,'quantity_send':quantity_send}


class Shipping_Control(models.Model):
	code = models.IntegerField()
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, related_name="employee")
	destination = models.CharField(max_length = 150)
	active = models.BooleanField(default = True)
	on_rute = models.BooleanField(default = False)
	date = models.DateTimeField(auto_now_add = True)
	employee_who_receives = models.ForeignKey(Employee, on_delete = models.CASCADE, related_name="employee_who_receives")
	





class PaymentMethod(models.Model):
    cash_closing = models.ForeignKey(Cash_Closings, related_name='payment_methods', on_delete=models.CASCADE)
    method_name = models.CharField(max_length=50)  # Nombre del método de pago (ej. Efectivo, Tarjeta)
    amount = models.FloatField(default=0)  # Monto pagado con esta forma

    def __str__(self):
        return f"{self.method_name}: {self.amount}"