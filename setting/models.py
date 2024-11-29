from django.db.models import Sum
from datetime import datetime, date
from django.db import models
import json, requests, env, base64, io

class Unit_Measures(models.Model):
    id_unit = models.IntegerField(unique = True)
    name = models.CharField(max_length = 191)

    def __str__(self):
        return f"{self.id_unit} - {self.name}"

    @classmethod
    def create_unit_measures(cls, data):
        value = cls(id_unit = data['id'], name = data['name'])
        value.save()

    @classmethod
    def get_unit_measures(cls):
        return [
            {
                'id': i.id_unit,
                'name':i.name
            }
            for i in cls.objects.all().order_by('name')
        ]

class Operation(models.Model):
    url_api = models.CharField(max_length = 255)

class BANK_NAME(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

class Transaction_Types(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

class Book_Account(models.Model):
    name = models.CharField(max_length = 80)

    def __str__(self):
        return self.name

class Book_Account_Type(models.Model):
    name = models.CharField(max_length = 80)
    book_account = models.ForeignKey(Book_Account, on_delete= models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.book_account.name}'


class Municipalities(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 35)

    def __str__(self):
        return self.name

    @classmethod
    def get_municipalities(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Document_I(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 150)

    def __str__(self):
        return self.name

    @classmethod
    def get_type_document_i(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Document(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return f'ID: {self.id} - DOC: {self.name}'

    @classmethod
    def get_type_document(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Organization(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

    @classmethod
    def get_type_organization(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Regimen(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_type_regimen(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Contract(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_type_contract(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Payroll_Type_Document_Identification(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_payroll_type_document_identification(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Sub_Type_Worker(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_sub_type_worker(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Worker(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_type_worker(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Payment_Form(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

class Payment_Method(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name
        
class Permission(models.Model):
    _id = models.IntegerField(default = 1)
    name = models.CharField(max_length = 255)

    def __str__(self):
        return self.name

    @classmethod
    def get_list_permission(cls):
        return [
            {
                'pk_permission' : i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]


class Send_Dian:
    def __init__(self, invoice):
        self.invoice = invoice

    def Error_Handling(self):
        message = None
        if self.days < 0:
            message = "La fecha de vencimiento o fecha de factura "


    def Data(self):
        tiempo_objeto = datetime.strptime(self.invoice['time'], "%H:%M:%S.%f")
        time = tiempo_objeto.strftime("%H:%M:%S")
        return {
            "number": self.invoice['number'],
            "type_document_id": self.type_document_id,
            "date": str(self.invoice['date']) if self.type_document_id == 1 else str(date.today()),
            "time": str(time),
            "resolution_number": self.invoice['resolution']['resolution'],
            "prefix": self.invoice['prefix'],
            "notes": self.invoice['note'],
            "establishment_name": self.invoice['branch']['name'],
            "establishment_address": self.invoice['branch']['address'],
            "establishment_phone": self.invoice['branch']['phone'],
            "establishment_municipality": 1,
            "establishment_email": self.invoice['branch']['email'],
            "disable_confirmation_text": False,
            "sendmail": True,
            "sendmailtome": True,
            "send_customer_credentials": True,
            "email_cc_list": [
                {
                    "email": "evansoft.test@gmail.com"
                },
                {
                    "email": "evansoft.test@hotmail.com"
                }
            ],
            "head_note": "",
            "foot_note": "Esta factura fue realizada por Evansoft",
            "logo_url":self.invoice['company']['logo_url'],
            "html_header": r'<h1 style=\"color: #5e9ca0;\">Se&ntilde;or(es), XXXXXXXXXXXXXXXXXXX identificado con NIT 99999999-9</h1><h2 style=\"color: #2e6c80;\">Le informamos que ha recibido un documento electronico de: YYYYYYYYYYYYYYYYYYYYYYYYY</h2>',
            "html_buttons": r'<table style=\"border-collapse: collapse; width: 100%;\" border=\"1\"><tbody><tr><td style=\"width: 100%;\"><h2><strong><span style=\"color: #008080;\">Puede descargar su factura mediante el siguiente enlace:</span></strong></h2></td></tr><tr><td style=\"width: 100%;\"><h4><a href=\"https://www.facilwebnube.com/apidian2021/public/index.php/api/download/88261176/FES-FE369.pdf\" target=\"_blank\">Haga click aqui para descargar su factura.</a></h4></td></tr></tbody></table>',
            "html_footer": r'<table style=\"border-collapse: collapse; width: 100%;\" border=\"1\"><tbody><tr><td style=\"width: 100%;\"><h2><strong><span style=\"color: #008080;\">Previamente recibio un correo con las credenciales de ingreso a la plataforma.</span></strong></h2></td></tr><tr><td style=\"width: 100%;\"><div><h4><strong>Este es un sistema autom&aacute;tico de aviso, por favor no responda este mensaje de correo.</strong></h4></div></td></tr></tbody></table>',
        }

    def Billing_Reference(self):
        return {
            "number": str(self.invoice['number']),
            "uuid": self.invoice['cufe'],
            "issue_date": self.invoice['date']
        }

    def Customer(self):
        if str(self.invoice['customer']['identification_number']) == "222222222222":
            return {
                "identification_number": 222222222222,
                "name": "CONSUMIDOR FINAL",
                "phone": self.invoice['branch']['phone'],
                "address": self.invoice['branch']['address'],
                "email": self.invoice['branch']['email'],
                "municipality_id":self.invoice['branch']['municipality'],
                "type_regime_id": self.invoice['customer']['type_regime']
            }
        else:
            return {
                "identification_number": int(self.invoice['customer']['identification_number']),
                "dv": self.invoice['customer']['dv'],
                "name": self.invoice['customer']['name'],
                "phone": self.invoice['customer']['phone'] if self.invoice['customer']['phone'] is not None else "12345678",
                "address": self.invoice['customer']['address'] if self.invoice['customer']['address'] is not None else "No tiene",
                "email": self.invoice['customer']['email'],
                "merchant_registration": "0000000-00",
                "type_document_identification_id": self.invoice['customer']['type_document_i'],
                "type_organization_id": self.invoice['customer']['type_organization'],
                "type_liability_id": 14,
                "municipality_id": self.invoice['customer']['municipality'],
                "type_regime_id": self.invoice['customer']['type_regime'],
                "postal_zone_code": 630001
            }

    def count_days(self, due_date):
        return (datetime.strptime(due_date, "%Y-%m-%d") - datetime.strptime(self.invoice['date'], "%Y-%m-%d")).days + 1

    def Payment_Form(self):
        self.days = self.count_days(self.invoice['payment_form']['payment_due_date'])
        return {
            "payment_form_id": self.invoice['payment_form']['payment_form'],
            "payment_method_id": self.invoice['payment_form']['payment_method'],
            "payment_due_date": self.invoice['payment_form']['payment_due_date'],
            "duration_measure": 0
        }

    def sum_value(self, item):
        return sum(int(round(i[f'{item}'])) * round(int(i['quantity'])) for i in self.invoice['details'])

    def Legal_Monetary_Totals(self):
        subtotal = self.sum_value('cost')
        ipo = self.sum_value('ipo')
        self.total_invoice = subtotal + ipo + self.sum_value('tax')        
        
        return {
            "line_extension_amount": subtotal,
            "tax_exclusive_amount": subtotal,
            "tax_inclusive_amount": self.total_invoice,
            "allowance_total_amount": '0',
            "charge_total_amount": '0',
            "payable_amount": self.total_invoice
        }

    def values_taxes(self,tax):
        total_base = 0
        total_tax = 0
        for item in self.invoice['details']:
            if int(tax) == int(item['tax_value']) and int(tax) != 45:
                total_tax += round((item['tax']  * item['quantity']))
                total_base += round(item['cost'] * item['quantity'])
            if int(item['ipo']) > 0 and int(tax) == 45:
                total_tax += round((item['ipo']  * item['quantity']))
                total_base += round((item['price'] * item['quantity']))
                self.quantity_ipo = item['quantity']
                self.ipo_unit = item['ipo']
        return {str(tax): total_tax, 'base': total_base}

    def Tax_Totals(self):
        taxes = []
        tax_19 = self.values_taxes(19)
        tax_5 = self.values_taxes(5)
        tax_0 = self.values_taxes(0)
        ipo_value = self.values_taxes(45)

        if tax_19['base'] > 0:
            taxes.append({
                "tax_id": 1,
                "tax_amount": str(tax_19['19']),
                "percent": "19",
                "taxable_amount": str(tax_19['base'])
            })
        if tax_5['base'] > 0:
            taxes.append({
                "tax_id": 1,
                "tax_amount": str(tax_5['5']),
                "percent": "5",
                "taxable_amount": str(tax_5['base'])
            })
        if tax_0['base'] > 0:
            taxes.append({
                "tax_id": 1,
                "tax_amount": str(tax_0['0']),
                "percent": "0",
                "taxable_amount": str(tax_0['base'])
            })
        if int(ipo_value['base']) > 0:
            taxes.append(
                {
                    "tax_id": 15,
                    "tax_amount": int(ipo_value['45']),
                    "percent": "0",
                    "taxable_amount": "0",
                    "unit_measure_id": "70",
                    "per_unit_amount": self.quantity_ipo,
                    "base_unit_measure": self.ipo_unit,
                    "tax_name":"Impuesto al consumo"
                }
            )
        return taxes

    def Invoice_Lines(self):
        data = []
        for i in self.invoice['details']:
            quantity = float(i['quantity'])
            cost = round( (float(i['cost']) + float(i['tax'])) * quantity)
            tax = round(float(i['tax']) * quantity)
            ipo = round(float(i['ipo']) * quantity)
            total =  round(float(i['subtotals'] + tax))
            subtotal = round(float(i['price']) * quantity )
            
            data.append(
                {
                    "ipo": ipo,
                    "unit_measure_id": 70,
                    "invoiced_quantity": quantity,
                    "line_extension_amount": subtotal,
                    "free_of_charge_indicator": False,
                    "tax_totals": [
                        {
                            "tax_id": 1,
                            "tax_amount": tax,
                            "taxable_amount": subtotal,
                            "percent": i['tax_value']
                        }, {
                            "tax_id": 15,
                            "tax_amount": ipo,
                            "percent": "0",
                            "taxable_amount": "0",
                            "unit_measure_id": "70",
                            "per_unit_amount": quantity,
                            "base_unit_measure": round(float(i['ipo'])),
                            "tax_name": "Impuesto al consumo"
                        }
                    ],
                    "description": i['name'],
                    "notes": '',
                    "code": i['code'],
                    "type_item_identification_id": 4,
                    "price_amount": total,
                    "base_quantity": quantity,
                    "neto": total
                }
            )
        return data

    def Software_Manufacturer(self):
        return {
            "name": "ALEXANDER OBANDO LONDONO",
            "business_name": "TORRE SOFTWARE",
            "software_name": "BABEL"
        }

    def Buyer_Benefits(self):
        return {
            "code": "89008003",
            "name": "INVERSIONES DAVAL SAS",
            "points": "100"
        }

    def Cash_Information(self):
        return {
            "plate_number": "DF-000-12345",
            "location": "HOTEL OVERLOOK RECEPCION",
            "cashier": "JACK TORRANCE",
            "cash_type": "CAJA PRINCIPAL",
            "sales_code": "EPOS1",
            "subtotal": srtr(self.total_invoice)
        }


    def Send(self, type_document, invoice):
        result = False
        messages = None
        invoice = invoice
        if self.invoice['company']['verified']:
            self.type_document_id = type_document
            production = self.invoice['company']['production']
            document = "invoice" if production else f"invoice/{self.invoice['company']['testsetid']}"
            key_invoice = 'invoice_lines'
            key_customer = "customer"

            if type_document == 11:
                document = "support-document"
                key_customer = "seller"
            elif type_document == 4:
                document = "credit-note"
                key_invoice = "credit_note_lines"
            elif type_document == 5:
                document = "debit-note"
                key_invoice = "debit_note_lines"
            elif int(type_document) == 15:
                document = "eqdoc/no_test_set_id"

            url = f"{env.URL_API}{document}"
            data = self.Data()
            if type_document != 4:
                data['payment_form'] = self.Payment_Form()
            data['legal_monetary_totals'] = self.Legal_Monetary_Totals()
            data['tax_totals'] = self.Tax_Totals()
            data[key_customer] = self.Customer()
            data[key_invoice] = self.Invoice_Lines()

            if type_document == 4 or type_document == 5:
                data['billing_reference'] = self.Billing_Reference()
            if int(type_document) == 15:
                data['software_manufacturer'] = self.Software_Manufacturer()
                data['buyer_benefits'] = self.Buyer_Benefits()
                data['cash_information'] = self.Cash_Information()

            if type_document == 11:
                for i in data['invoice']:
                    print(i)
            payload = json.dumps(data)
            headers = {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'Authorization': f'Bearer {self.invoice["company"]["token"]}'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            _response = json.loads(response.text)
            with open(f"{env.ERRORES}response_dian.txt",'w') as file:
                file.write(str(response.text))
            result = False
            messages = []
            if production:
                with open(f"{env.ERRORES}production.txt",'w') as file:
                    file.write(str(response.text))
                if 'errors' in _response:
                    for i,j in _response['errors'].items():
                        messages.append(_response['errors'][i][0])
                else:
                    messages = _response['message']
                    values = _response['ResponseDian']['Envelope']['Body']['SendBillSyncResponse']['SendBillSyncResult']
                    if type_document == 4:
                        invoice.urlinvoicexml_nc = str(_response['urlinvoicexml'])
                        invoice.urlinvoicepdf_nc = str(_response['urlinvoicepdf'])
                        if str(_response['urlinvoiceattached']) != '':
                            invoice.attacheddocument_nc = str(_response['urlinvoiceattached'])
                            result = True
                        invoice.QRStr_nc = str(_response['QRStr'])
                        invoice.cude = _response['cude']
                        messages = values['StatusDescription']
                        invoice.state = messages
                        invoice.branch.company.certificate_days_left = str(_response['certificate_days_left'])
                        invoice.save()
                    else:
                        invoice.branch.company.certificate_days_left = str(_response['certificate_days_left'])
                        invoice.urlinvoicexml = str(_response['urlinvoicexml'])
                        invoice.urlinvoicepdf = str(_response['urlinvoicepdf'])
                        if str(_response['urlinvoiceattached']) != '':
                            invoice.attacheddocument = str(_response['urlinvoiceattached'])
                            result = True
                        invoice.QRStr = str(_response['QRStr'])
                        invoice.cufe = _response['cufe']
                        messages = values['StatusDescription']
                        invoice.state = messages
                        invoice.save()
            else:
                invoice.urlinvoicexml = str(_response['urlinvoicexml'])
                invoice.urlinvoicepdf = str(_response['urlinvoicepdf'])
                invoice.attacheddocument = str(_response['urlinvoiceattached'])
                invoice.QRStr = str(_response['QRStr'])
                invoice.cufe = _response['cufe']
                result = True
                invoice.save()
            data = {'token':f'Bearer {self.invoice["company"]["token"]}', 'pdf': f"{self.invoice['company']['documentI']}/{_response['urlinvoicepdf']}",'prefix':self.invoice['prefix'],'number':self.invoice['number'],
                        'email':[{'email':self.invoice['branch']['email']}] if str(self.invoice['customer']['identification_number']) == "222222222222" else [{'email':self.invoice['branch']['email'],'email': self.invoice['customer']['email']}]}
        else:
            messages = "ERROR, ESTA COMPAÑIA NO ESTA EN VERIFICADA"
            print("Error")
        return {'result':result, 'message':messages}

    def pdf_to_base64(self, input_pdf_path: str) -> str:
        try:
            with open(f"C:/laragon/www/apidian/storage/app/public/{input_pdf_path}", "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            base64_string = base64.b64encode(pdf_bytes).decode('utf-8')
            return base64_string
        except Exception as e:
            print(f"Error al convertir PDF a Base64: {e}")
            return ""

    def Send_Emial(self,data):
        pdf = self.pdf_to_base64(data['pdf'])
        payload = json.dumps({
          "prefix": data['prefix'],
          "number": str(data['number']),
          "showacceptrejectbuttons": False,
          "email_cc_list": data['email'],
          "base64graphicrepresentation": f"{pdf}"
        })
        headers = {
          'Content-Type': 'application/json',
          'accept': 'application/json',
          'Authorization': f'{data["token"]}'
        }
        url = f"{env.URL_API}send-email"
        response = requests.request("POST", "http://159.203.170.123:8080/api/ubl2.1/send-email", headers=headers, data=payload)
        print(response)
        pritn(response.status_code)
        pritn(response.text)
        print("Hola cabron")

    
        

class Credi_Note_Product:
    def __init__(self, invoice, product, quantity, type_discrepancy, discrepancy_description, number_resolution):
        self.invoice = invoice
        self.product = product
        self.quantity = quantity
        self.type_discrepancy = type_discrepancy
        self.discrepancy_description = discrepancy_description
        self.number_resolution = number_resolution

    def header(self):
        return {
            "discrepancyresponsecode": self.type_discrepancy,
            "discrepancyresponsedescription": self.discrepancy_description,
            "notes": "PRUEBA DE NOTA CREDITO",
            "resolution_number": "0000000000",
            "prefix": "NCP",
            "number": self.number_resolution,
            "type_document_id": 4,
            "date": f"{date.today()}",
            "time": f"{datetime.now().strftime('%H:%M:%S')}",
            "establishment_name": self.invoice['branch']['name'],
            "establishment_address": self.invoice['branch']['address'],
            "establishment_phone": self.invoice['branch']['phone'],
            "establishment_municipality": 1,
            "establishment_email": self.invoice['branch']['email'],
            "seze": "2021-2017",
            "foot_note": "Esta factura fue realizada por Evansoft",
        }

    def sum_value(self, item):
        return sum(int(round(i[f'{item}'])) * round(int(i['quantity'])) for i in self.invoice['details'] if i['code'] == self.product)

    def Legal_Monetary_Totals(self):
        for i in self.invoice['details']:
            if i['code'] == self.product:
                subtotal = self.sum_value('price')
                ipo = self.sum_value('ipo')
                total_invoice = subtotal + self.sum_value('tax') + ipo        
                return {
                    "line_extension_amount": subtotal,
                    "tax_exclusive_amount": subtotal,
                    "tax_inclusive_amount": total_invoice,
                    "allowance_total_amount": '0',
                    "charge_total_amount": '0',
                    "payable_amount": total_invoice
                }

    def Customer(self):
        if str(self.invoice['customer']['identification_number'])[0:10] == "2222222222":
            return {
                "identification_number": 222222222222,
                "name": "CONSUMIDOR FINAL",
                "merchant_registration": "0000000-00"
            }
        else:
            return {
                "identification_number": self.invoice['customer']['identification_number'],
                "dv": self.invoice['customer']['dv'],
                "name": self.invoice['customer']['name'],
                "phone": self.invoice['customer']['phone'] if self.invoice['customer']['phone'] is not None else "12345678",
                "address": self.invoice['customer']['address'] if self.invoice['customer']['address'] is not None else "No tiene",
                "email": self.invoice['customer']['email'],
                "merchant_registration": "0000000-00",
                "type_document_identification_id": self.invoice['customer']['type_document_i'],
                "type_organization_id": self.invoice['customer']['type_organization'],
                "type_liability_id": 14,
                "municipality_id": self.invoice['customer']['municipality'],
                "type_regime_id": self.invoice['customer']['type_regime'],
                "postal_zone_code": 630001
            }

    def count_days(self, due_date):
        return (datetime.strptime(due_date, "%Y-%m-%d") - datetime.strptime(self.invoice['date'], "%Y-%m-%d")).days

    def Payment_Form(self):
        self.days = self.count_days(self.invoice['payment_form']['payment_due_date'])
        return {
            "payment_form_id": 1,
            "payment_method_id": 10,
            "payment_due_date": str(date.today()),
            "duration_measure": 0
        }

    def Billing_Reference(self):
        print(self.invoice['cufe'])
        return {
            "number": f'{self.invoice["prefix"]}{self.invoice["number"]}',
            "uuid": self.invoice['cufe'],
            "issue_date": self.invoice['date']
        }

    def values_taxes(self,tax):
        total_base = 0
        total_tax = 0
        for item in self.invoice['details']:
            if item['code'] == self.product:
                if int(tax) == int(item['tax_value']):
                    total_tax += round((item['tax']  * item['quantity']))
                    total_base += round((item['price'] * item['quantity']))
                if int(tax) == 15:
                    total_tax += round((item['ipo']  * item['quantity']))
                    total_base += round((item['price'] * item['quantity']))
        return {str(tax): total_tax, 'base': total_base}

    def Tax_Totals(self):
        taxes = []
        for i in self.invoice['details']:
            if i['code'] == self.product:
                tax_19 = self.values_taxes(19)
                tax_5 = self.values_taxes(5)
                tax_0 = self.values_taxes(0)
                ipo_value = self.values_taxes(15)

                if tax_19['base'] != 0:
                    taxes.append({
                        "tax_id": 1,
                        "tax_amount": str(tax_19['19']),
                        "percent": "19",
                        "taxable_amount": str(tax_19['base'])
                    })
                if tax_5['base'] != 0:
                    taxes.append({
                        "tax_id": 1,
                        "tax_amount": str(tax_5['5']),
                        "percent": "5",
                        "taxable_amount": str(tax_5['base'])
                    })
                if tax_0['base'] != 0:
                    taxes.append({
                        "tax_id": 1,
                        "tax_amount": str(tax_0['0']),
                        "percent": "0",
                        "taxable_amount": str(tax_0['base'])
                    })
                if int(ipo_value['base']) != 0:
                    taxes.append(
                        {
                            "tax_id": 15,
                            "tax_amount": str(ipo_value['15']),
                            "taxable_amount": str(ipo_value['base']),
                            "percent": 0,
                            "tax_name": "Nada"
                        }
                    )
        return taxes

    def Credit_Note_Lines(self):
        data = []
        for i in self.invoice['details']:
            if i['code'] == self.product:
                quantity = float(i['quantity'])
                cost = round(float(i['price']) * quantity)
                tax = round(float(i['tax']) * quantity)
                ipo = round(float(i['ipo']) * quantity)

                total =  (cost + tax + ipo)
                
                data.append(
                    {
                        "unit_measure_id": 70,
                        "invoiced_quantity": quantity,
                        "line_extension_amount": cost,
                        "free_of_charge_indicator": False,
                        "tax_totals": [
                            {
                                "tax_id": 1,
                                "tax_amount": tax,
                                "taxable_amount": cost,
                                "percent": i['tax_value']
                            },
                            {
                                "tax_id": 15,
                                "tax_amount": ipo,
                                "taxable_amount": cost,
                                "percent": 0,
                                "tax_name": "Nada"
                            }
                        ],
                        "description": i['name'],
                        "notes": '',
                        "code": i['code'],
                        "type_item_identification_id": 4,
                        "price_amount": total,
                        "base_quantity": quantity,
                        "type_generation_transmition_id": 1,
                        "start_date": "2023-05-01"
                    }
                )
        return data

    def Send(self):
        url = f"{env.URL_API}credit-note/not_test_set_id"
        data = self.header()
        data['billing_reference'] = self.Billing_Reference()
        data['payment_form'] = self.Payment_Form()
        data['legal_monetary_totals'] = self.Legal_Monetary_Totals()
        data['tax_totals'] = self.Tax_Totals()
        data["customer"] = self.Customer()
        data["credit_note_lines"] = self.Credit_Note_Lines()
        payload = json.dumps(data)
        headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': f'Bearer {self.invoice["company"]["token"]}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = json.loads(response.text)
        result = False
        messages = []
        if 'errors' in response:
            for i,j in response['errors'].items():
                messages.append(response['errors'][i][0])
        else:
            print(response)
            result = True
        return {'result':result, 'message':messages, 'data': response, 'cude': response['cude']}
