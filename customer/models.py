from setting.models import *
from django.db import models
from company.models import Branch
from user.models import Employee
from django.core import serializers
import json

class Customer(models.Model):
	identification_number = models.IntegerField()
	dv = models.IntegerField(default = 0)
	name = models.CharField(max_length = 100)
	phone = models.CharField(max_length = 12,null=True, blank=True)
	address = models.CharField(max_length = 150,null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	email_optional = models.EmailField(null=True, blank=True)
	type_document_i = models.ForeignKey(Type_Document_I, on_delete = models.CASCADE)
	type_organization = models.ForeignKey(Type_Organization, on_delete = models.CASCADE)
	municipality = models.ForeignKey(Municipalities, on_delete = models.CASCADE)
	type_regime = models.ForeignKey(Type_Regimen, on_delete = models.CASCADE)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)

	def __str__(self):
		return f"{self.name} - {self.branch.name}"


	@staticmethod
	def dv_client(rut):
	    factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
	    rut_ajustado=str(rut).rjust( 15, '0')
	    s = sum(int(rut_ajustado[14-i]) * factores[i] for i in range(14)) % 11
	    if s > 1:
	        return 11 - s
	    else:
	        return s

	@classmethod
	def delete_client(cls, data):
		result = False
		message = None
		try:
			cls.objects.get(pk = data['pk_customer']).delete()
			result = True
			message = "Success"
		except cls.DoesNotExist as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def create_customer(cls, data):
		result = False
		message = None
		branch = Employee.objects.get(pk = data['pk_employee']).branch
		try:
			customer = cls.objects.get(identification_number = data['identification_number'], branch = branch)
			message = "The client already exists"
		except Exception as e:
			customer = cls(
				identification_number = data['identification_number'],
				dv = cls.dv_client(data['identification_number']),
				name = data['name'],
				phone = data['phone'] if data['phone'] else None,
				address = data['address'] if data['address'] else None,
				email = data['email'] if data['email'] else None,
				type_document_i = Type_Document_I.objects.get(pk = data['type_document_identification_id'] if data['type_document_identification_id'] else 1),
				type_organization = Type_Organization.objects.get(pk = data['type_organization_id'] if data['type_organization_id'] else 1),
				municipality = Municipalities.objects.get(pk = data['municipality_id'] if data['municipality_id'] else 1),
				type_regime = Type_Regimen.objects.get(pk = data['type_regime_id'] if data['type_regime_id'] else 1),
				branch = branch
			)
			customer.save()
			result = True
			message = "Success"
		return {'result':result, 'message':message}

	@classmethod
	def create_consumidor_final(cls, branch):
		customer = cls(
			identification_number = 222222222222,
			dv = 2,
			name = "CONSUMIDOR FINAL",
			type_document_i = Type_Document_I.objects.get(pk = 1),
			type_organization = Type_Organization.objects.get(pk = 1),
			municipality = Municipalities.objects.get(pk = 1),
			type_regime = Type_Regimen.objects.get(pk = 1),
			branch = branch
		)
		customer.save()


	@classmethod
	def update_customer(cls, data):
		result = False
		message = None
		try:
			customer = cls.objects.get(pk = data['pk_customer'])
			customer.identification_number = data['identification_number']
			customer.dv = cls.dv_client(data['identification_number'])
			customer.name = data['name']
			customer.phone = data['phone']
			customer.address = data['address']
			customer.email = data['email']
			customer.email_optional = data['email_optional']
			customer.type_document_i = Type_Document_I.objects.get(pk = data['type_document_identification_id'])
			customer.type_organization = Type_Organization.objects.get(pk = data['type_organization_id'])
			customer.municipality = Municipalities.objects.get(pk = data['municipality_id'])
			customer.type_regime = Type_Regimen.objects.get(pk = data['type_regime_id'])
			customer.save()
			result = True
			message = "Success"
		except cls.DoesNotExist as e:
			customer = None
			message = str(e)
		return {'result':result, 'message':message}


	@staticmethod
	def serializers_data(obj):
		serialized_customer = serializers.serialize('json', [obj])
		return json.loads(serialized_customer)[0]

	@classmethod
	def get_list_customer(cls, data):
		branch = Employee.objects.get(pk = data['pk_employee']).branch
		list_customer = []
		for i in cls.objects.filter(branch = branch):
			customer = cls.serializers_data(i)
			data = customer['fields']
			data['pk_customer'] = customer['pk']
			list_customer.append(data)
		return list_customer


	@classmethod
	def get_customer(cls, data):
		customer = cls.serializers_data(cls.objects.get(pk = data['pk_customer']))
		data = customer['fields']
		data['name_type_document_i'] = Type_Document_I.objects.get(pk = data['type_document_i']).name
		data['name_type_organization'] = Type_Organization.objects.get(pk = data['type_organization']).name
		data['name_municipality'] = Municipalities.objects.get(pk = data['municipality']).name
		data['name_type_regime'] = Type_Regimen.objects.get(pk = data['type_regime']).name
		data['pk_customer'] = customer['pk']
		return data
		

class Wallet_Customer(models.Model):
	amount = models.IntegerField()
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	note = models.TextField()
	date_register = models.DateField(auto_now_add= True)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
	coin = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def update_wallet_customer(cls, data):
		result = False
		message = None
		try:
			wallet_c = cls.objects.get(customer=Customer.objects.get(pk = data['pk_customer']))
			wallet_c.amount += data['amount']
			wallet_c.save()
		except Exception as e:
			print(e)
		return {'result':result, 'message':message}

	@classmethod
	def update_coins(cls, data):
		result = False
		message = None
		wallet_c = None
		try:
			customer = Customer.objects.get(pk = data['pk_customer'])
			if data['amount_invoice'] >= customer.branch.amount_min:
				wallet_c = cls.objects.get(customer = customer)
				wallet_c.coin += int(data['amount_invoice'] / customer.branch.value_coin)
				wallet_c.save()
				result = True
				message = "Success"
		except Exception as e:
			print(e)
		return {'result':result, 'message':message,'coin_generate':wallet_c.coin if wallet_c is not None else None}


