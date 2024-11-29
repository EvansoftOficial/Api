from django.db import IntegrityError
from inventory.models import Product, Supplier
from setting.models import Payment_Form, Payment_Method
from django.core import serializers
from company.models import Branch, License
from user.models import Employee
from django.db import models
import json, math

class Shopping(models.Model):
	number = models.CharField(max_length = 50, unique = True)
	date = models.DateTimeField(auto_now_add = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE) 
	date_registration = models.CharField(max_length = 10)
	cancelled = models.BooleanField(default = True)
	annulled = models.BooleanField(default = False)
	total = models.FloatField(null = True, blank = True)

	def __str__(self):
		return f"{self.number} by {self.branch.name} - {self.date}"

	@staticmethod
	def values_taxes(cls,invoice,tax):
		total_base = 0
		total_tax = 0
		for item in invoice:
		    if int(tax) == int(item['tax']) and int(tax) != 45:
		        total_tax += round((item['amount_tax']  * item['quantity']))
		        total_base += round((item['cost'] ) * item['quantity'])

		    if int(item['ipo']) > 0 and int(tax) == 45:
		        total_tax += round((item['ipo']  * item['quantity']))
		        total_base +=  round((item['cost'] ) * item['quantity'])
		        cls.quantity_ipo = item['quantity']
		        cls.ipo_unit = item['ipo']

		return {str(tax): total_tax, 'base': total_base}

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
	def verified_invoice(cls, data):
		result = False
		message = None
		try:
			cls.objects.get(number=data['number'], branch = Employee.objects.get(pk = data['pk_employee']).branch)
			result = True
			message = "Esta factura de compra ya existe."
		except cls.DoesNotExist as e:
			message = None
		return {'result':result, 'message':message}

	@staticmethod
	def serializers_obj(obj):
		return json.loads(serializers.serialize('json', [obj]))

	@classmethod
	def get_invoice_shopping(cls, data):
	    result = False
	    message = None
	    _data = []
	    try:
	        shopping = cls.objects.filter(branch=data['pk_branch']).order_by('-pk')
	        for i in shopping:
	            obj = cls.serializers_obj(i)[0]['fields']
	            obj['pk_shopping'] = i.pk
	            obj['supplier'] = Supplier.objects.get(pk=obj['supplier']).name
	            
	            # Verifica si 'total' es un float y aplica math.ceil() con un pequeño ajuste
	            if isinstance(obj['total'], (int, float)):
	                original_total = obj['total']
	                # obj['_total'] = math.ceil(float(obj['total']) + 0.00001)  # Agrega una pequeña fracción
	                obj['total'] = math.ceil(float(obj['total']) / 100) * 100
	                print(f"Redondeando total: Original: {original_total}, Redondeado: {obj['total']}")
	            else:
	                obj['total'] = obj['total']  # En caso de que no sea un número válido
	            
	            _data.append(obj)
	        result = True
	        message = 'Success'
	    except Exception as e:
	        message = str(e)
	    return {'result': result, 'message': message, 'data': _data}

	@classmethod
	def get_invoice_shopping_pk(cls,data):
		result = False
		message = None
		_data = []
		try:
			shopping = cls.objects.get(branch = data['pk_branch'], number = data['number'])
			_data = cls.serializers_obj(shopping)[0]['fields']
			_supplier = Supplier.objects.get(pk = _data['supplier'])
			if isinstance(_data['total'], (int, float)):
			    original_total =_data['total']
			    _data['total'] = math.ceil(float(_data['total']) / 100) * 100
			    print(f"Redondeando total: Original: {original_total}, Redondeado: {_data['total']}")
			else:
			    _data['total'] = _data['total'] 
			value_details = []
			for i in Details.objects.filter( shopping = shopping):
				_details = cls.serializers_obj(i)[0]['fields']
				value_tax = 1 + (int(_details['tax']) / 100)
				total = round(float(_details['cost']) * value_tax) * _details['quantity']
				amount_tax = total - (total / value_tax)
				_details['subtotal'] = round(_details['cost'] * _details['quantity'])
				if isinstance(total, (int, float)):
				    original_total =total
				    total = math.ceil(float(total) / 100) * 100
				    print(f"Redondeando total: Original: {original_total}, Redondeado: {total}")
				else:
				    total = total 
				_details['total_row'] = total
				_details['amount_tax'] = amount_tax

				value_details.append(_details)
			_data['details'] = value_details
			_data['PaymentFormShopping'] = cls.serializers_obj(PaymentFormShopping.objects.get( shopping = shopping))[0]['fields']
			_data['supplier'] = cls.serializers_obj(_supplier)[0]['fields']
			_data['branch'] = cls.serializers_obj(Branch.objects.get(pk = _data['branch']))[0]['fields']
			_data['list_taxes'] = cls.Tax_Totals(cls,_data['details'])
			result = True
			message = 'Success'
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'data':_data}

	@classmethod
	def create_shopping(cls, data):
		result = False
		message = None
		total = 0
		try:
			branch = Branch.objects.get(pk=data['pk_branch']) if 'pk_branch' in data else Employee.objects.get(pk=data['pk_employee']).branch
			value = License.discount_license(branch)
			if value['result']:
				shopping = cls(
					number = data['number'],
					branch = branch,
					supplier = Supplier.objects.get(pk = data['pk_supplier']),
					date_registration = data['date_registration'],
				)
				shopping.save()
				result = True
				message = "Success"
				for i in data['details']:
					result = Details.create_details(i, shopping)
					total += result['total']
					if not result['result']:
						message = result['message']
						result = result['result']
						break
				result = PaymentFormShopping.create_payment_form(data, shopping)
				shopping.total = total
				shopping.save()
				if not result['result']:
					message = result['message']
					result = result['result']
				else:
					result = result['result']
			else:
				result = value['result']
				message = value['message']
		except IntegrityError as inte:
			message = "This invoice has already been registered."
		except Exception as e:
			message = f"{e} - Shopping Invoice"
		return {'result':result, 'message':message}


class Details(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.IntegerField()
	cost = models.FloatField()
	price_1 = models.FloatField()
	price_2 = models.FloatField()
	price_3 = models.FloatField()
	ipo = models.FloatField()
	ultra_processed = models.FloatField(default = 0)
	discount = models.FloatField()
	shopping = models.ForeignKey(Shopping, on_delete = models.CASCADE)

	def __str__(self):
		return f"{self.shopping.number} by {self.shopping.branch.name} - {self.shopping.date}"

	@classmethod
	def create_details(cls,data,shopping):
		result = False
		message = None
		total = 0
		try:
			details = cls(
				code= data['code'],
			    name= data['name'],
			    quantity= data['quantity'],
			    tax= data['tax'],
			    cost= data['cost'],
			    price_1= data['price_1'],
			    price_2= data['price_2'],
			    price_3= data['price_3'],
			    ipo= data['ipo'],
			    ultra_processed = data['ultra_processed'] if 'ultra_processed' in data else 0,
			    discount= data['discount'],
			    shopping= shopping
			)
			details.save()
			result = True
			message= "Success"
			if result:
				result = cls.update_product_by_shopping(data, shopping)
				print(result,'result product')
			total += round(float(data['total_cost']) * float(data['quantity']))
			message = result['message']
			result = result['result']
		except Exception as e:
			message = str(e)
			print(e)
		return {'result':result, 'message':message,'total':total}


	@staticmethod
	def update_product_by_shopping(data, shopping):
		result = False
		message = None
		try:
			product = Product.objects.get(code = data['code'], branch = shopping.branch)
			product.tax = data['tax']
			quantity = int(data['quantity'])
			if product.quantity_static > 0:
				if product.bale_quantity <= 0:
					product.quantity += quantity - product.quantity_static
					product.bale_quantity += product.bale_quantity_static
					if product.quantity_unit <= 0:
						product.bale_quantity -= 1
						product.quantity_unit += product.quantity_unit_static
				else:
					product.quantity += quantity
				print(product.quantity)
			elif product.bale_quantity_static > 0:
				if product.quantity_unit <= 0:
					product.bale_quantity += (quantity - product.bale_quantity_static)
					product.quantity_unit += product.quantity_unit_static
				else:
					product.bale_quantity += quantity
			elif product.quantity_unit_static > 0:	
				product.quantity_unit_static += int(data['quantity'])
			elif product.quantity_static == 0 and product.bale_quantity_static == 0 and product.quantity_unit_static == 0:
				product.quantity_unit += int(data['quantity'])

			print(quantity)
			product.price_1 = data['price_1']
			product.price_2 = data['price_2']
			product.price_3 = data['price_3']
			product.price_4 = data['price_4']
			product.price_5 = data['price_5']
			product.price_6 = data['price_6']
			product.ultra_processed = data['ultra_processed'] if 'ultra_processed' in data else 0
			product.ipo = data['ipo']
			product.discount = data['discount']
			product.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}


class PaymentFormShopping(models.Model):
	shopping = models.ForeignKey(Shopping, on_delete = models.CASCADE)
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 10)

	def __str__(self):
		return f"{self.shopping.number} by {self.shopping.branch.name} - {self.shopping.date}"

	@classmethod
	def create_payment_form(cls, data, shopping):
		result = False
		message = None
		try:
			payment_form = cls(
				shopping = shopping,
				payment_form = Payment_Form.objects.get(_id = data['payment_form']['pk_paymentform']),
				payment_method = Payment_Method.objects.get(_id = data['payment_form']['pk_paymentmethod']),
				payment_due_date = data['payment_form']['payment_due_date']
			)
			payment_form.save()
			employee = Employee.objects.get(pk = data['pk_employee'])
			if int(data['payment_form']['pk_paymentform']) == 2:
				shopping.cancelled = False
				shopping.save()
				_data = {
					"pk_shopping": shopping.pk,
					"amount":0,
					"note":"There are no pass yet",
					"pk_employee": employee.pk
				}
				Pass.create_pass(_data)
				result = True
				message = "Success"
			serialized_product = serializers.serialize('json', [employee])
			employee = json.loads(serialized_product)[0]['fields']
			serialized_supplier = serializers.serialize('json', [shopping.supplier])
			supplier = json.loads(serialized_supplier)[0]['fields']
			serialized_shopping = serializers.serialize('json', [shopping])
			_shopping = json.loads(serialized_shopping)[0]['fields']
			print("Hola")
			value = History_Shopping.create_history(_shopping, supplier, employee)
			print(value)
			result = value['result']
			message = value['message']
		except Exception as e:
			message = str(e)+" employee not found"
		return {'result':result, 'message':message}

class Pass(models.Model):
	number_pass = models.IntegerField()
	shopping = models.ForeignKey(Shopping, on_delete = models.CASCADE)
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
		shopping = Shopping.objects.get(pk = data['pk_shopping'])
		result = False
		message = None
		try:
			_pass = cls.objects.get(shopping = shopping)
			if _pass.amount < shopping.total:
				if float(data['amount']) <= (shopping.total - _pass.amount) and float(data['amount']) > 0:
					_pass.amount += float(data['amount'])
					message = "Credit to the invoice was accepted"
					result = True
					_pass.save()
				else:
					message = "You cannot pay more than the total invoice"
		except cls.DoesNotExist as e:
			_pass = cls(
				number_pass = number if number > 0 else 1,
				shopping = shopping,
				amount = data['amount'],
				note = data['note']
			)
			message = f"Credit to the invoice {shopping.number} was created successfully"
			result = True
			_pass.save()
		if _pass.amount == shopping.total:
			shopping.cancelled = True
			shopping.save()
			message = "The invoice has already been canceled"

		serialized_invoice = serializers.serialize('json', [shopping])
		serialized_supplier = serializers.serialize('json', [shopping.supplier])
		employee = Employee.objects.get(pk = data['pk_employee'])
		serialized_product = serializers.serialize('json', [employee])
		employee = json.loads(serialized_product)[0]['fields']
		supplier = json.loads(serialized_supplier)[0]['fields']
		shopping = json.loads(serialized_invoice)[0]['fields']
		if result:
			History_Pass.create_history_pass(shopping,data['amount'], supplier,data['note'], employee, data['transaction'] if 'transaction' in data else None)
		return {'result':True, 'message':message}

	@classmethod
	def cancel_all_invoices(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		supplier = Supplier.objects.get(pk = data['pk_supplier'])
		shopping = Shopping.objects.filter(branch= employee.branch, cancelled = False, supplier = supplier)
		total = 0
		result = False
		message = None
		amount = data['amount']
		for i in shopping:
			total += i.total
		if total == amount:
			for i in shopping:
				_pass = cls.objects.get(shopping = i)
				_pass.amount = i.total
				_pass.save()
				i.cancelled = True
				i.save()
				result = True
				message = "Invoice paid"
		else:
			note = None
			for i in shopping:
				if amount >= i.total:
					_pass = cls.objects.get(shopping = i)
					_pass.amount = i.total
					amount -= i.total
					i.cancelled = True
					_pass.save()
					note = "Pago factura"
					serialized_shopping = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.supplier])
					supplier = json.loads(serialized_customer)[0]['fields']
					_shopping = json.loads(serialized_shopping)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_shopping, data['amount'], supplier, note , __employee)
					result = True
					message = "Invoice paid"
				else:
					_pass = cls.objects.get(shopping = i)
					_pass.amount += amount
					_pass.save()
					note = "Abona a la factura"
					serialized_shopping = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.supplier])
					supplier = json.loads(serialized_customer)[0]['fields']
					_shopping = json.loads(serialized_shopping)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_shopping, data['amount'], supplier, note , __employee)
					result = True
					message = "Invoice paid"
					if not _pass.shopping.cancelled:
						amount -= _pass.amount
						if amount <= 0:
							break
				i.save()
		
		return {'result':result, 'message':message,"returned_value":amount}


class History_Shopping(models.Model):
	shopping = models.JSONField(null = True, blank = True)
	employee = models.JSONField(null = True, blank = True)
	supplier = models.JSONField(null = True, blank = True)
	date_registration = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return f"Number: {self.shopping['number']} - Proveedor: {self.supplier['name']} by {self.employee['user_name'].capitalize()} - {self.date_registration} "

	@classmethod
	def create_history(cls,shopping, supplier, employee):
		result = False
		message = None
		try:
			hs = cls(
				shopping = shopping,
				supplier = supplier,
				employee = employee
			)
			hs.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message}

class History_Pass(models.Model):
	shopping = models.JSONField(null = True, blank = True)
	amount = models.FloatField(null = True, blank = True)
	customer = models.JSONField(null = True, blank = True)
	employee = models.JSONField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	number_transaction = models.CharField(max_length = 50,default = 0,null = True, blank = True)
	date_registration = models.DateTimeField(auto_now_add = True)

	@classmethod
	def create_history_pass(cls, shopping, amount, customer, note, employee, trasaction = None):
		result = False
		message = None
		try:
			hp = cls(
				shopping = shopping,
				amount = amount,
				customer = customer,
				note = note,
				employee = employee,
				number_transaction = trasaction if trasaction is not None else None
			)
			hp.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}