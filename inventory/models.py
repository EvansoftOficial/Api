from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import IntegrityError
from django.core import serializers
from datetime import date as _date
from company.models import Branch
from django.db import transaction
from django.db.models import Sum
from user.models import Employee
from django.db.models import Q
from django.db import models
from setting.models import *
import json, env

class Supplier(models.Model):
	documentI = models.IntegerField(null = True, blank = True)
	name = models.CharField(max_length = 70)
	email = models.EmailField(null = True, blank = True)
	phone = models.CharField(max_length = 15,null = True, blank = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	address = models.TextField(null = True, blank = True)
	merchant_registration = models.CharField(max_length = 30,null = True, blank = True)
	postal_zone_code = models.IntegerField(null = True, blank = True)
	type_document_identification_id = models.ForeignKey(Type_Document_I, on_delete = models.CASCADE,null = True, blank = True)
	municipality_id = models.ForeignKey(Municipalities, on_delete = models.CASCADE,null = True, blank = True)
	type_liability_id = models.IntegerField(null = True, blank = True)
	type_regime_id = models.ForeignKey(Type_Regimen, on_delete = models.CASCADE, null = True, blank = True)


	def __str__(self):
		return f"{self.name} by {self.branch.name}"

	@classmethod
	def create_supplier(cls,data):
		result = True
		message = None
		try:
			supplier = cls(
				documentI = data['documentI'],
				name = data['name'],
				email = data['email'],
				phone = data['phone'],
				branch = Employee.objects.get(pk = data['pk_employee']).branch
			)
			supplier.save()
			message = "Successs"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message}


	@classmethod
	def create_supplier_general(cls, branch):
		result = True
		message = None
		try:
			supplier = cls(
				name = "Proveedor General",
				branch = branch
			)
			supplier.save()
			message = "Successs"
		except Exception as e:
			message = str(e)
			print(e)
		return {'result': result, 'message':message}

	@classmethod
	def update_supplier(cls,data):
		result = True
		message = None
		try:
			supplier = cls.objects.get(pk = data['pk_supplier'])
			supplier.documentI = data['documentI']
			supplier.name = data['name']
			supplier.email = data['email']
			supplier.phone = data['phone']
			supplier.save()
			message = "Successs"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message}

	@classmethod
	def list_supplier(cls, data):
		branch = Employee.objects.get(pk = data['pk_employee']).branch
		return [
			{
				"pk": i.pk,
				"documentI": i.documentI if i.documentI else "No tiene",
				"name": i.name,
				"email": i.email if i.email else "No tiene",
				"phone": i.phone if i.phone else "No tiene"
			}
			for i in cls.objects.filter(branch = branch)
		]

	@classmethod
	def list_supplier_company(cls, branch):
		return [
			{
				"pk": i.pk,
				"documentI": i.documentI if i.documentI else "No tiene",
				"name": i.name,
				"email": i.email if i.email else "No tiene",
				"phone": i.phone if i.phone else "No tiene"
			}
			for i in cls.objects.filter(branch = branch)
		]

	@classmethod
	def get_supplier(cls,data):
		return json.loads( serializers.serialize('json', [cls.objects.get(pk = data['pk_supplier'])]))[0]['fields']

	@classmethod
	def delete_supplier(cls,data):
		branch = Employee.objects.get(pk = data['pk_employee']).branch
		result = True
		message = None
		try:
			cls.objects.get(branch = branch, pk = data['pk_suppplier']).delete()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

class Category(models.Model):
	name = models.CharField(max_length = 150, unique= True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)

	def __str__(self):
		return f"{self.name} - {self.branch.name}"

	@classmethod
	def create_category(cls,data):
		result = False
		message = None 
		category = None 
		try:
			category = cls(name = data['name'].lower(), branch = Branch.objects.get(pk = data['pk_branch']))
			category.save()
			result = True
			message = "Successfully registered category"
		except IntegrityError as inte:
			message = "There is already a category with the same name"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message, 'category_pk': category.pk}

	@classmethod
	def get_list_category(cls, data):
		return [
			{
				'pk_category':i.pk,
				'name': i.name
			}
			for i in cls.objects.filter(branch = Branch.objects.get(pk = data['pk_branch'])).order_by('name')
		]

class SubCategory(models.Model):
	name = models.CharField(max_length = 150)
	category = models.ForeignKey(Category, on_delete = models.CASCADE)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)

	def __str__(self):
		return self.name

	@classmethod
	def create_subcategory(cls,data):
		message = None
		result = False
		subcat = None
		try:
			subcat = cls(name = data['name'].lower(),category=Category.objects.get(pk = data['pk_category']))
			subcat.save()
			message = "Successfully registered subcategory"
			result = True
		except IntegrityError:
			message = "There is already a subcategory with the same name"
		except Exception as e:
			message = str(e)
		return {'message':message, 'result':result, 'subcategory':subcat.pk}

	@classmethod
	def create_subcategory_branch(cls,data,branch):
		message = None
		result = False
		subcat = None
		try:
			category = Category.objects.get(name = data['name_category'].lower())
			subcat = cls(name = data['name'].lower(),category=category,branch = branch)
			subcat.save()
			message = "Successfully registered subcategory"
			result = True
		except IntegrityError:
			message = "There is already a subcategory with the same name"
		except Exception as e:
			message = str(e)
		return {'message':message, 'result':result, 'subcategory':subcat.pk}


	@classmethod
	def get_list_subcategory(cls, data):
		list_sub = []
		category = Category.objects.get(pk = data['pk_category'])
		for i in cls.objects.filter(category = category).order_by('name'):
			serialized_subcategory = serializers.serialize('json', [i])
			subc = json.loads(serialized_subcategory)
			data = subc[0]['fields']
			data['pk_sub'] = subc[0]['pk']
			list_sub.append(data)
		return list_sub

class Product(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	quantity_unit = models.IntegerField(default=0, null = True, blank = True)
	bale_quantity = models.IntegerField(default=0, null = True, blank = True)

	quantity_static = models.IntegerField(default=0)
	quantity_unit_static = models.IntegerField(default=0, null = True, blank = True)
	bale_quantity_static = models.IntegerField(default=0, null = True, blank = True)

	price_1 = models.FloatField()
	price_2 = models.FloatField(default=0)
	price_3 = models.FloatField(default=0)
	price_4 = models.FloatField(default=0)
	price_5 = models.FloatField(default=0)
	price_6 = models.FloatField(default=0)

	tax = models.IntegerField()
	cost = models.FloatField()
	ipo = models.FloatField()
	ultra_processed = models.FloatField(default = 0)
	discount = models.FloatField()
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	subcategory = models.ForeignKey(SubCategory, on_delete = models.CASCADE, null = True, blank = True)
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE, null = True, blank = True)
	unit_measures = models.ForeignKey(Unit_Measures, on_delete = models.CASCADE, null = True, blank = True)
	percentages = models.IntegerField(default = 0, null = True, blank = True)

	@classmethod
	def validated_quantity(cls, data):
	    print("Entre")
	    result = False
	    message = None

	    print(f"Datos recibidos: {data}")
	    
	    try:
	        employee = Employee.objects.get(pk=data['pk_employee'])
	        branch = employee.branch
	        product = cls.objects.get(pk=data['code'])

	        print(f"Producto encontrado: {product}")
	        print(f"Cantidad del producto: quantity_unit={product.quantity_unit}, bale_quantity={product.bale_quantity}, quantity={product.quantity}")
	        
	        if 'type_price' not in data:
	            return {
	                'result': False,
	                'message': "No se proporcionó el tipo de precio"
	            }

	        type_price = int(data['type_price'])
	        print(f"Tipo de precio recibido: {type_price}")

	        if type_price == 1 or type_price == 4:
	            print("Entré en la condición de type_price 1 o 4")
	            print(f"Comparando: product.quantity_unit({product.quantity_unit}) < data['quantity']({int(data['quantity'])})")
	            if product.quantity_unit < int(data['quantity']):
	                if product.bale_quantity > 0:
	                    print("Iniciando recarga de unidades con bale_quantity")
	                    while product.quantity_unit < int(data['quantity']) and product.bale_quantity > 0:
	                        product.quantity_unit += product.quantity_unit_static
	                        product.bale_quantity -= 1
	                        result = True
	                        message = "Units were recharged"
	                        print(f"Unidades recargadas: quantity_unit={product.quantity_unit}, bale_quantity={product.bale_quantity}")
	                elif product.quantity > 0:
	                    print("Iniciando recarga de unidades con quantity")
	                    while product.quantity_unit < int(data['quantity']) and product.quantity > 0:
	                        product.quantity -= 1
	                        product.bale_quantity += product.bale_quantity_static
	                        product.bale_quantity -= 1
	                        product.quantity_unit += product.quantity_unit_static
	                        result = True
	                        message = "Units were recharged"
	                        print(f"Unidades recargadas: quantity={product.quantity}, bale_quantity={product.bale_quantity}, quantity_unit={product.quantity_unit}")
	                else:
	                    message = "There is no product to recharge the units"
	                    result = True
	            else:
	            	result = True
	            	message = "Todavia hay unidades"
	        elif type_price == 2 or type_price == 5:
	            print("Entré en la condición de type_price 2 o 5")
	            if product.bale_quantity <= int(data['quantity']):
	                if product.quantity > 0:
	                    print("Iniciando recarga de paquetes")
	                    while product.bale_quantity < int(data['quantity']) and product.quantity > 0:
	                        product.quantity -= 1
	                        product.bale_quantity += product.bale_quantity_static
	                        result = True
	                    message = "Packages were reloaded"
	                    print(f"Paquetes recargados: quantity={product.quantity}, bale_quantity={product.bale_quantity}")
	            else:
	                message = "ENTRE AQUIIIII"
	        else:
	            message = "It does not have a box to recharge"
	        
	        product.save()

	        print(f"Mensaje final: {message}")
	        return {
	            'result': result,
	            'message': message,
	            "quantity": product.quantity,
	            "bale_quantity": product.bale_quantity,
	            "quantity_unit": product.quantity_unit
	        }
	    
	    except Employee.DoesNotExist:
	        return {
	            'result': False,
	            'message': "Empleado no encontrado"
	        }
	    
	    except cls.DoesNotExist:
	        return {
	            'result': False,
	            'message': "Producto no encontrado"
	        }





	def __str__(self):
		return f"Product: {self.name} - Branch: {self.branch.name}"

	def calculate_profit_percentages(self):
		profit_percentages = {}
		prices = {
			'price': self.price,
			'price2': self.price2,
			'price3': self.price3,
			'price4': self.price4,
			'price5': self.price5,
			'price6': self.price6
		}
		for price_field, price in prices.items():
			price = price / (1 + (self.tax / 100))
			profit = (price - self.cost) * self.quantity
			profit_percentage = (profit / (self.cost * self.quantity)) * 100
			profit_percentages[price_field] = profit_percentage
		return profit_percentages

	@staticmethod
	def calculate_profit_amount(self):
	    profit_amounts = {}
	    prices = {
			'Price 1': self.price_1,
			'Price 2': self.price_2,
			'Price 3': self.price_3,
			'Price 4': self.price_4,
			'Price 5': self.price_5,
			'Price 6': self.price_6
		}

	    for price_field, price in prices.items():
	        try:
	        	price = price / (1 + (self.tax / 100))
	        	profit_percentage = ((price - self.cost) / price) * 100
	        	profit_amount = (profit_percentage / 100) * price  # Calculate the amount of profit in money
	        	profit_amounts[price_field] = profit_amount
	        except ZeroDivisionError as e:
	            profit_amounts[price_field] = 0
	    return profit_amounts

	def calculate_profit_percentages_one_quantity(self):
		profit_percentages = []
		prices = {
			'Price 1': self.price_1,
			'Price 2': self.price_2,
			'Price 3': self.price_3,
			'Price 4': self.price_4,
			'Price 5': self.price_5,
			'Price 6': self.price_6
		}
		n = 1
		for price_field, price in prices.items():
		    try:
		    	price = price / (1 + (self.tax / 100))
		    	discounted_price = price - (price * (self.discount / 100))
		    	if discounted_price == self.cost:
		    		profit_percentage = 0
		    	else:
		    		profit_percentage = (((discounted_price - self.cost) / discounted_price) * 100)
		    	profit_percentages.append({
		            'percentage': f'{profit_percentage:.1f}%',
		            'name': price_field,
		            'id': n
		        })
		    except ZeroDivisionError as e:
		        profit_percentages.append({
		            'percentage': '0%',
		            'name': price_field,
		            'id': n
		        })
		    n += 1

		return profit_percentages

	@staticmethod
	def Delete_Product_All(cls, branch):
		for i in cls.objects.filter(branch = branch):
			i.delete()

	@classmethod
	def create_product(cls,data):
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		supplier = None
		subcat = None
		try:
			with open(f'{env.ERRORES}product.txt','w') as product:
				product.write(str(data))
			try:
				if 'pk_supplier' in data:
					supplier = Supplier.objects.get(pk = data['pk_supplier'], branch=branch)
				else:
					supplier = Supplier.objects.get(name = 'Proveedor General', branch=branch)
					
				if 'pk_subcategory' in data:
					subcat = SubCategory.objects.get(pk = data['pk_subcategory'])
				else:
					subcat = SubCategory.objects.get(name = data['category'].lower())
			except Exception as e_code:
				with open(f'{env.ERRORES}error_sub.txt','w') as product:
					product.write(str(e_code))
				with open(f'{env.ERRORES}error_subcategory.txt','w') as product:
					product.write(str(data['category'].lower()))

			
			if data['excel'] == 1:
				cls.Delete_Product_All(cls, branch)
			try:
				code = data['code']
				try:
					code = str(data['code']).split(',')[0]
				except Exception as e_code:
					with open(f'{env.ERRORES}e_code.txt','w') as product:
						product.write(str(e_code))
				product = cls.objects.get(code = code, branch = branch)
				message = "This product is already registered"
			except cls.DoesNotExist as e:
				product = None
			unit_measures = Unit_Measures.objects.get(id_unit = 70)

			if product is None:
				try:
					product = cls(
					    code= data['code'],
					    name= str(data['name']).upper(),
					    quantity= data['quantity'],
					    quantity_unit= data['quantity_unit'],
					    bale_quantity= data['bale_quantity'],
					    quantity_static= data['quantity_static'],
					    quantity_unit_static= data['quantity_unit_static'],
					    bale_quantity_static= data['bale_quantity_static'],
					    tax= data['tax'],
					    cost= data['cost'],
					    price_1= data['price_1'],
					    price_2= data['price_2'],
					    price_3= data['price_3'],
					    price_4= data['price_4'],
					    price_5= data['price_5'],
					    price_6= data['price_6'],
					    ipo= data['ipo'],
					    ultra_processed= data['ultra_processed'] if 'ultra_processed' in data else 0,
					    discount= data['discount'],
					    branch= employee.branch,
					    subcategory= subcat,
					    supplier= supplier,
					    unit_measures= unit_measures,
					    percentages= data['percentages'] if 'percentages' in data else 0
					)

					product.save()
					result = True
					branch = employee.branch
					message = "Success"
					serialized_employee = serializers.serialize('json', [employee])
					employee = json.loads(serialized_employee)
					History_Product.register_movement('Created', {}, data, employee ,branch)
				except Exception as e:
					message = str(e)
					with open(f'{env.ERRORES}register_product.txt','w') as f:
						f.write(str(e))
		except Exception as ex:
			with open(f'{env.ERRORES}create_product.txt','w') as f:
				f.write(str(ex))
		return {'result': result, 'message': message}

	@classmethod
	def update_product(cls, data):
	    result = False
	    message = None
	    employee = Employee.objects.get(pk=data['pk_employee'])
	    branch = employee.branch

	    try:
	        product = cls.objects.get(pk=data['pk_product'])
	    except cls.DoesNotExist as e:
	        message = str(e)
	        product = None

	    if product is not None:
	        original_values = json.loads(serializers.serialize('json', [product]))[0]['fields']
	        try:
	            product.code = data['code']
	            product.name = str(data['name']).upper()
	            product.quantity = data['quantity']
	            product.quantity_unit = data['quantity_unit']
	            product.bale_quantity = data['bale_quantity']
	            product.quantity_static = data['quantity_static']
	            product.quantity_unit_static = data['quantity_unit_static']
	            product.bale_quantity_static = data['bale_quantity_static']
	            product.tax = data['tax']
	            product.cost = data['cost']
	            product.price_1 = data['price_1']
	            product.price_2 = data['price_2']
	            product.price_3 = data['price_3']
	            product.price_4 = data['price_4']
	            product.price_5 = data['price_5']
	            product.price_6 = data['price_6']
	            product.ipo = data['ipo']
	            product.ultra_processed = data['ultra_processed']
	            product.discount = data['discount']
	            product.branch = branch
	            product.unit_measures = Unit_Measures.objects.get(id_unit = data['unit_measures']) if 'unit_measures' in data else Unit_Measures.objects.get(id_unit = 70)
	            product.subcategory = SubCategory.objects.get(pk=data['pk_subcategory'])
	            product.supplier = Supplier.objects.get(pk=data['pk_supplier'])
	            product.percentages = data['percentages']
	            product.save()
	            result = True
	            message = "Success"
	            serialized_employee = serializers.serialize('json', [employee])
	            employee = json.loads(serialized_employee)
	            modified_values = {}
	            for key, value in data.items():
	                try:
	                	if original_values[key].lower() != value.lower() or float(original_values[key]) != value:
	                		modified_values[key] = original_values[key]
	                except Exception as e:
	                	pass
	            History_Product.register_movement('Modified', modified_values, data, employee, branch)
	        except Exception as e:
	            message = str(e)
	            print(e)
	    return {'result': result, 'message': message}

	@classmethod
	def delete_product(cls,data):
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		try:
			_product = cls.objects.get(pk = data['pk_product'])
			message = "Existo"
			serialized_employee = serializers.serialize('json', [employee])
			employee = json.loads(serialized_employee)
			serialized_product = serializers.serialize('json', [_product])
			product = json.loads(serialized_product)[0]['fields']
			History_Product.register_movement('Deleted',{}, product, employee ,branch)
			_product.delete()
			result = True
			message = 'Success'
		except cls.DoesNotExist as e:
			message = str(e)
			product = None
			print(e)
		return {'result':result, 'message':message}

	@classmethod
	def discount_product(cls,pk_product, branch, quantity, employee,json):
		result = False
		message = None
		try:
			if not json:
				pr = Product_Reserved.objects.get(user = employee, product= cls.objects.get(pk = pk_product))
				print(pr)
				pr.delete()
			Best_Selling_Product.best_selling_product(pk_product, branch, quantity)
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
			print(e)
		return {'result': result, 'message':message}

	@classmethod
	def get_list_products(cls, data):
		list_products = []
		try:
			branch = Employee.objects.get(pk = data['pk_employee']).branch
			for i in cls.objects.filter(branch = branch).order_by('name'):
				product = serialized_employee = serializers.serialize('json', [i])
				product = json.loads(product)[0]['fields']
				# product['category'] = i.subcategory.category.name
				product['name_branch'] = i.branch.name
				product['pk_product'] = i.pk
				list_products.append(product)
		except Exception as e:
			print(e)		
		return list_products

	@classmethod
	def get_list_products_company(cls, data):
		list_products = []
		try:
			branch = Branch.objects.get(pk = data['pk_branch'])
			for i in cls.objects.filter(branch = branch):
				product = serialized_employee = serializers.serialize('json', [i])
				print(i.pk)
				_product = json.loads(product)[0]['fields']
				_product['pk_product'] = i.pk
				list_products.append(_product)
		except Exception as e:
			print(e)		
		return list_products

	@classmethod
	def get_list_products_supplier(cls, data):
		branch = Employee.objects.get(pk = data['pk_employee']).branch
		list_products = []
		for i in cls.objects.filter(branch = branch, supplier = Supplier.objects.get(pk = data['pk_supplier'])):
			product = serializers.serialize('json', [i])
			product = json.loads(product)[0]['fields']
			product ['total_cost'] = cls.calculate_cost(product)
			product ['pk_product'] = i.pk
			list_products.append(product)
		return list_products

	@staticmethod
	def calculate_cost(data):
		cost = float(data['cost']) * float(1 + int(data['tax']) / 100)
		return cost + float(data['ipo'])

	@classmethod
	def get_product(cls, data):
		_data = []
		try:
			print(data)
			pk_employee = data['pk_employee']
			_product = cls.objects.get(pk = data['code'])
			product = serialized_employee = serializers.serialize('json', [_product])
			_data = json.loads(product)[0]['fields']
			_data['pk_cat'] = SubCategory.objects.get(pk = _data['subcategory']).category.pk
			_data['category'] = SubCategory.objects.get(pk = _data['subcategory']).category.name
			_data['pk_subcategory'] = SubCategory.objects.get(pk = _data['subcategory']).pk
			_data['subcategory'] = SubCategory.objects.get(pk = _data['subcategory']).name
			_data['pk_supplier'] = Supplier.objects.get(pk = _data['supplier']).pk
			_data['supplier'] = Supplier.objects.get(pk = _data['supplier']).name
			_data['calculate_profit_percentages'] = cls.calculate_profit_percentages_one_quantity(_product)
			_data['calculate_profit_amount'] = cls.calculate_profit_amount(_product)
			_data['pk_category'] = _data['pk_cat']
			_data['name_category'] = Category.objects.get( pk = _data['pk_cat']).name
			_data['list_category'] = Category.get_list_category({'pk_branch':_product.branch.pk})
			_data['unit_measures_name'] = Unit_Measures.objects.get( pk = _data['unit_measures']).name
			_data['list_subcategory'] = SubCategory.get_list_subcategory(_data)
			_data['pk_employee'] = pk_employee
			_data['pk_product'] = _product.pk
			_data['list_supplier'] = Supplier.list_supplier(_data)
			_data['total_cost'] = round(cls.calculate_cost(_data),2)
		except Exception as e:
			print(e)		
		return _data

	@classmethod
	def get_product_company(cls, data):
		_data = []
		try:
			_product = cls.objects.get(pk = data['pk_product'])
			product = serialized_employee = serializers.serialize('json', [_product])
			_data = json.loads(product)[0]['fields']
			_data['pk_cat'] = SubCategory.objects.get(pk = _data['subcategory']).category.pk
			_data['category'] = SubCategory.objects.get(pk = _data['subcategory']).category.name
			_data['pk_subcategory'] = SubCategory.objects.get(pk = _data['subcategory']).pk
			_data['subcategory'] = SubCategory.objects.get(pk = _data['subcategory']).name
			_data['pk_supplier'] = Supplier.objects.get(pk = _data['supplier']).pk
			_data['supplier'] = Supplier.objects.get(pk = _data['supplier']).name
			_data['calculate_profit_percentages'] = cls.calculate_profit_percentages_one_quantity(_product)
			_data['calculate_profit_amount'] = cls.calculate_profit_amount(_product)
			_data['pk_category'] = _data['pk_cat']
			_data['name_category'] = Category.objects.get( pk = _data['pk_cat']).name
			_data['list_category'] = Category.get_list_category({'pk_branch':_product.branch.pk})
			_data['unit_measures_name'] = Unit_Measures.objects.get( pk = _data['unit_measures']).name
			_data['list_subcategory'] = SubCategory.get_list_subcategory(_data)
			_data['list_supplier'] = Supplier.list_supplier_company(_product.branch)
			_data['total_cost'] = round(cls.calculate_cost(_data),2)
			_data['pk_product'] = _product.pk
		except Exception as e:
			print(e,'Error')		
		return _data


	@classmethod
	@database_sync_to_async
	def create_multiple(cls,data):
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		supplier = None
		subcat = None
		print(data)
		try:
			try:
				if 'pk_supplier' in data['products']:
					supplier = Supplier.objects.get(pk = 31, branch=branch)
				else:
					supplier = Supplier.objects.get(name = 'Proveedor General', branch=branch)
					
				if 'pk_subcategory' in data['products']:
					subcat = SubCategory.objects.get(pk = 16)#i['pk_subcategory']
			except Exception as e_code:
				print(e_code)
			
			unit_measures = Unit_Measures.objects.get(id_unit = 70)
			try:
				product = []
				existing_codes = []
				list_product_ = []
				cls.objects.filter(branch=employee.branch).delete()
				with transaction.atomic():
					cls.objects.filter(branch=employee.branch).delete()
				for i in data['products']:
					list_product_.append(i)
					print(i)
					try:
					    if str(i['code']).strip() in existing_codes:
					        print(f"El código {str(i['code']).strip()} ya ha sido agregado previamente. Se omite este producto.")
					    else:
					    	existing_codes.append(str(i['code']).strip())
					    	product.append(
							    cls(
							        code=str(i['code']).strip(),
							        name=str(i['name']).upper(),
							        quantity=i['quantity'],
							        quantity_unit=i['quantity_unit'],
							        bale_quantity=i['bale_quantity'],
							        quantity_static=i['quantity_static'],
							        quantity_unit_static=i['quantity_unit_static'],
							        bale_quantity_static=i['bale_quantity_static'],
							        tax=i['tax'],
							        cost=i['cost'],
							        price_1=i['price_1'],
							        price_2=i['price_2'],
							        price_3=i['price_3'],
							        price_4=i['price_4'],
							        price_5=i['price_5'],
							        price_6=i['price_6'],
							        ipo=i['ipo'],
							        ultra_processed=i['ultra_processed'] if 'ultra_processed' in i else 0,
							        discount=i['discount'],
							        branch=employee.branch,
							        subcategory= SubCategory.objects.get(name = i['category'].lower()),
							        supplier=Supplier.objects.get(name = 'Proveedor General', branch=branch),
							        unit_measures=unit_measures,
							        percentages=i['percentages'] if 'percentages' in i else 0
							    )
							)
					except Exception as error:
					    print(error)
				cls.objects.bulk_create(product)
				result = True
				branch = employee.branch
				message = "Success"
				serialized_employee = serializers.serialize('json', [employee])
				employee = json.loads(serialized_employee)
				History_Product.register_movement('Created', {}, data, employee ,branch)
			except Exception as e:
				print(e,'error',i)
				message = str(e)
				with open(f'{env.ERRORES}register_product.txt','w') as f:
					f.write(str(e))
		except Exception as ex:
			print(ex,'ERROR CREATE_MULTIPLE')
			with open(f'{env.ERRORES}create_product.txt','w') as f:
				f.write(str(ex))
		return {'result': result, 'message': message}



	@classmethod
	@database_sync_to_async
	def filter_product(cls, data):
		result = False
		message= None
		list_product = []
		try:
			list_product = [
				{
					"value": i.pk,
					"label": i.name,
				}
				for i in cls.objects.filter(name__icontains = data['name'])
			]
			result = True
			message = "Successful search"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message': message, 'list_product': list_product}


	@classmethod
	@database_sync_to_async
	def get_product_by_code(cls, pk):
		try:
			product = cls.objects.get(pk=pk)
			data = cls.get_obj_serialized(product)
			print(data)
			return {
				'result': True,
				'product': data,
			}
		except cls.DoesNotExist:
			return {'result': False, 'message': 'Producto no encontrado'}
		except Exception as e:
			return {'result': False, 'message': str(e)}

	@staticmethod
	def get_obj_serialized(obj):
	    try:
	        serialized_obj = serializers.serialize('json', [obj])
	        return json.loads(serialized_obj)[0]
	    except Employee.DoesNotExist:
	        return {'error': 'Employee not found'}


	@classmethod
	@database_sync_to_async
	def get_paginated_products(cls, page, per_page, pk_branch):
	    products = cls.objects.filter(branch = Branch.objects.get(pk = pk_branch)).order_by('name')  # O filtra según sea necesario
	    paginator = Paginator(products, per_page)
	    try:
	        products_page = paginator.page(page)
	        data = [
	            {
	                'code': product.code,
	                'name': product.name,
	                'unit_measures': product.unit_measures.name,
	                'unit': product.quantity_unit,
	                'bale_quantity': product.bale_quantity,
	                'quantity': product.quantity,
	                'price_1': product.price_1,
	                'price_2': product.price_2,
	                'price_3': product.price_3,
	                'tax': product.tax,
	                'ipo': product.ipo,
	                'pk_product': product.pk
	            }
	            for product in products_page
	        ]
	        return {
	            'result': True,
	            'products': data,
	            'has_next': products_page.has_next(),
	            'has_previous': products_page.has_previous()
	        }
	    except Exception as e:
	        return {'result': False, 'message': str(e)}




class Best_Selling_Product(models.Model):
	product = models.ForeignKey(Product, on_delete = models.CASCADE)
	date = models.CharField(max_length = 15)
	sold = models.IntegerField()
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)

	@classmethod
	def best_selling_product(cls, pk_product, branch, quantity):
		result = False
		message = None
		product = Product.objects.get(pk = pk_product)
		try:
			bsp = cls.objects.get(product = product, date = _date.today())
			bsp.sold += quantity
			bsp.save()
			result = True
			message = "Best Selling Product Update"
		except cls.DoesNotExist as e:
			bsp = cls(
				product = product,
				date = _date.today(),
				sold = quantity,
				branch = branch
			)
			bsp.save()
			result = True
			message = "Best Selling Product Created"

		return {'result': result, 'message': message}

	


	@classmethod
	def get_best_selling_product(cls, data):
		result = False
		message = None
		quantity = 0
		try:
			product = Product.objects.get(code = data['code'],branch = data['pk_branch'])
			bsp = cls.objects.get(product = product, date = data['date'])
			result = True
			message = "Success"
			quantity = bsp.sold
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message,'quantity':quantity}

	@classmethod
	def get_list_best_selling_product(cls, data):
		result = False
		message = None
		_data = []
		total_sold = None
		print(data)
		try:
		    branch = Branch.objects.get(pk = data['pk_branch'])
		    start_date = data['start_date']
		    end_date = data['end_date']
		    queryset = cls.objects.filter(branch=branch)
		    if start_date and end_date:
		        queryset = queryset.filter(date__range=[start_date, end_date])
		    top_selling_products = queryset.values('product__name').annotate(total_sold=Sum('sold')).order_by('-total_sold')[:10]
		    total_sold = queryset.aggregate(Sum('sold'))['sold__sum']
		    for i in queryset:
		        serialized_data = json.loads(serializers.serialize('json', [i]))[0]
		        serialized_data['fields']['product_code'] = i.product.code
		        serialized_data['fields']['product_name'] = i.product.name
		        serialized_data['fields']['total_sold'] = total_sold
		        _data.append(serialized_data)
		    result = True
		    message = "Success"
		except Exception as e:
		    message = str(e)
		    print(e)
		print(data,'Data Seller')
		return {'result': result, 'message': message, 'data': _data}

	@classmethod
	def get_all_list_best_selling_product(cls, data):
		result = False
		message = None
		_data = []
		total_sold = None
		try:
		    branch = Branch.objects.get(pk=data['pk_branch'])
		    queryset = cls.objects.filter(branch=branch)
		    top_selling_products = queryset.values('product__name').annotate(total_sold=Sum('sold')).order_by('-total_sold')
		    for i in queryset:
		        serialized_data = json.loads(serializers.serialize('json', [i]))[0]
		        serialized_data['fields']['product_code'] = i.product.code
		        serialized_data['fields']['product_name'] = i.product.name
		        serialized_data['fields']['total_sold'] = total_sold
		        _data.append(serialized_data)
		    result = True
		    message = "Success"
		except Exception as e:
		    message = str(e)
		print(data,'Data')
		return {'result': result, 'message': message, 'data': _data}




from datetime import date
class History_Product(models.Model):
	ACTION_CHOICES = (
	    ('Created', 'Created'),
	    ('Modified', 'Modified'),
	    ('Deleted', 'Deleted')
	)
	action = models.CharField(max_length=10, choices=ACTION_CHOICES)
	product = models.JSONField()
	employee = models.JSONField()
	timestamp = models.CharField(max_length = 15, null = True, blank = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)
	modified_values = models.JSONField(null = True, blank = True)

	def __str__(self):
		return f"{self.product.get('name', 'N/A')} - {self.action} by {self.employee[0]['fields']['user_name'].capitalize()} - {self.timestamp} "

	@classmethod
	def register_movement(cls, action, modified_values, product, employee, branch):
		history_product = cls(
			action = action,
			product = product,
			employee = employee,
			modified_values = modified_values,
			branch = branch,
			timestamp = date.today()
		)
		history_product.save()

from django.db import transaction
class Product_Reserved(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	user = models.ForeignKey(Employee, on_delete = models.CASCADE)
	type_price = models.IntegerField(blank = True, null = True)

	@staticmethod
	def validated_quantity(product, data):
		if int(data['type_price']) == 1 or int(data['type_price']) == 4:
			if product.quantity_unit > 0:
				if product.quantity_unit >= int(data['quantity']):
					product.quantity_unit -= int(data['quantity'])
			else:
				if product.bale_quantity > 0:
					product.quantity_unit += product.quantity_unit_static
					product.bale_quantity -= 1
					product.quantity_unit -= int(data['quantity'])
				else:
					if product.quantity > 0:
						product.quantity -= 1
						product.bale_quantity += product.bale_quantity_static
						product.bale_quantity -= 1
						product.quantity_unit += product.quantity_unit_static
						product.quantity_unit -= int(data['quantity'])

	@classmethod
	def reserveding_product(cls,data):
		user = Employee.objects.get(pk = data['pk_user'])
		product = Product.objects.get(pk = data['pk_product'])
		result = False
		try:
			pr = cls.objects.get(product = product, user = user)
			pr.quantity += int(data['quantity'])
			pr.save()
		except cls.DoesNotExist as e:
			print(e,'Error')
			pr = None
		if pr is None:
			pr = cls(product= product, quantity= int(data['quantity']),user = user, type_price = int(data['type_price']))
			pr.save()
		if pr.quantity <= 0:
			pr.delete()

		if int(data['type_price']) == 1 or int(data['type_price']) == 4:
			product.quantity_unit -= int(data['quantity'])
		elif int(data['type_price']) == 2 or int(data['type_price']) == 5:
			product.bale_quantity -= int(data['quantity'])
		elif int(data['type_price']) == 3 or int(data['type_price']) == 6:
			product.quantity -= int(data['quantity'])

		try:
			product.save()
			result = True
		except Exception as e:
			print(f"Error retrieving or saving product reservation: {e}")
		return result

	@classmethod
	def return_products(cls,pk_user):
		pr = cls.objects.filter(user = Employee.objects.get(pk = pk_user))
		for i in pr:
			p = Product.objects.get(pk = i.product.pk)
			if i.type_price == 1 or i.type_price == 4:
				p.quantity_unit += i.quantity
			elif i.type_price == 2 or i.type_price == 5:
				p.bale_quantity += i.quantity
			elif i.type_price == 3 or i.type_price == 6:
				p.quantity += i.quantity
			p.save()
			i.delete()
		return True

	@classmethod
	def return_product_unique(cls, data):
	    user = Employee.objects.get(pk=data['pk_employee'])
	    product = Product.objects.get(pk=data['pk_product'], branch=user.branch)
	    with transaction.atomic():
	        _pr = cls.objects.get(product=product, user=user)
	        quantity = int(str(data['quantity']))
	        try:
	        	quantity = int(str(data['quantity']).replace('-',''))
	        except Exception as ex:
	        	pass

	        if _pr.type_price == 1 or _pr.type_price == 4:
	        	product.quantity_unit += _pr.quantity
	        elif _pr.type_price == 2 or _pr.type_price == 5:
	        	product.bale_quantity += _pr.quantity
	        elif _pr.type_price == 3 or _pr.type_price == 6:
	        	product.quantity += _pr.quantity
	        _pr.quantity -= quantity
	        _pr.save()
	        product.save()
	        if _pr.quantity <= 0:
	        	_pr.delete()
	    return True

class Loans(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	user = models.ForeignKey(Employee, on_delete = models.CASCADE)

