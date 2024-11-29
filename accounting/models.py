import os, env, glob, zipfile, pandas as pd
from datetime import datetime, timedelta
from django.http import HttpResponse
from inventory.models import Product
from company.models import Branch
from openpyxl import Workbook
from invoice.models import *
from django.db import models
from pathlib import Path



class AccountingEntry(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    sequence = models.IntegerField()  # Secuencia
    date_created = models.DateField()  # Fecha de elaboración
    accounting_code = models.CharField(max_length=30)  # Código contable
    accounting_account = models.CharField(max_length=100)  # Cuenta contable
    identification = models.CharField(max_length=20)  # Identificación (Cliente)
    description = models.TextField()  # Descripción
    debit = models.FloatField(default=0)  # Débito
    credit = models.FloatField(default=0)  # Crédito
    data = []
    total = 0
    number = None
    date = None

    def __str__(self):
        return f"Entry {self.sequence} for Invoice {self.invoice.number}"

    class Meta:
        verbose_name = 'Accounting Entry'
        verbose_name_plural = 'Accounting Entries'


    @classmethod
    def create_accountingentry(cls, data, invoice):
        result = False
        message = None
        print(data, invoice)
        try:
            for i in range(len(data)):
                accountingentry = cls(
                    invoice = invoice,
                    sequence = data[i]['sequence'],
                    date_created = data[i]['date_created'],
                    accounting_code = data[i]['accounting_code'],
                    accounting_account = data[i]['accounting_account'],
                    identification = data[i]['identification'],
                    description = data[i]['description'],
                    debit = round(data[i]['debit'],0),
                    credit = round(data[i]['credit'],0)
                )
                accountingentry.save()
                result = True
        except Exception as e:
            print(e,'create_accountingentry')
            message = str(e)
        return {'result': result, 'message': message}

    @staticmethod
    def Name_Category_Data(cls):
        cls.accounting_code = None
        cls.accounting_name = None

    @staticmethod
    def Taxes(cls):
        cls.tax_19_general = 0
        cls.tax_5_general = 0
        cls.ipo_0_general = 0
        cls.tax_19_gaseosa = 0
        cls.tax_19_licor = 0
        cls.ipo_19_licor = 0
        cls.tax_19_cerveza = 0
        cls.ipo_19_cerveza = 0
        cls.tax_19_vino = 0
        cls.ipo_19_vino = 0
        cls.tax_19_cigarrillo = 0
        cls.ipo_19_cigarrillo = 0
        cls.tax_19_bolsa = 0

    @staticmethod
    def Create_Document(cls, name_doc):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        encabezado = ["Secuencia", "Fecha elaboración", "Código contable", "Cuenta contable", 
                        "Identificación", "Descripción", "Débito", "Crédito"]
        sheet.append(encabezado)
        workbook.save(f"{name_doc}.xlsx")

    @staticmethod
    def Name_Category(cls,cat, tax, number, client, base, date):

        accounting_code = None
        accounting_name = None

        if  tax == 19 and "GENERAL" in cat.upper():
            accounting_code = 41350101
            accounting_name = 'VTA PRODU GNERAL 19%'

        elif tax == 5 and "GENERAL" in cat.upper():
            accounting_code = 41350102
            accounting_name = 'VTA PROD GNERL DEL 5%'

        elif tax == 0 and "GENERAL" in cat.upper():
            accounting_code = 41350103 
            accounting_name = 'VTA EXCENTA'

        elif tax == 19 and "GASEOSA" in cat.upper():
            accounting_code = 41350105
            accounting_name = 'VTA GASEOSA'

        elif tax == 5 and "LICOR" in cat.upper():
            accounting_code = 41350106
            accounting_name = 'VTA LICOR GNR DEL 5'

        elif tax == 19 and "CERVEZA" in cat.upper():
            accounting_code = 41350107
            accounting_name = 'VTA CERVEZA DEL 19'

        elif tax == 5 and "VINO" in cat.upper():
            accounting_code = 41350108 
            accounting_name = 'VTA VINO DEL 5'

        elif tax == 19 and "CIGARRILLO" in cat.upper():
            accounting_code = 41350109 
            accounting_name = 'VTA CIGARRILLO  DEL19'

        cls.data.append({
            'sequence':number,
            'date_created': date,
            'accounting_code': accounting_code,
            'accounting_account': accounting_name,
            'identification':client,
            'description':'Producto',
            'debit':0,
            'credit': base
        })

    @staticmethod
    def Calculate_Taxes(cls,ipo,tax,value,cat):
        if 19 == tax and cat.upper() == "GENERAL":
            cls.tax_19_general += round(float(value))

        elif 5 == tax and cat.upper() == "GENERAL":
            cls.tax_5_general += round(float(value))

        elif 0 == tax and cat.upper() == "GENERAL":
            cls.ipo_0_general += round(float(ipo))

        elif 19 == tax and cat.upper() == "GASEOSA":
            cls.tax_19_gaseosa += round(float(value))

        elif 5 == tax and cat.upper() == "LICOR":
            cls.tax_19_licor += round(float(value))
            cls.ipo_19_licor += round(float(ipo))
        
        elif 19 == tax and cat.upper() == "CERVEZA":
            cls.tax_19_cerveza += round(float(value))
            cls.ipo_19_cerveza += round(float(ipo))

        elif 5 == tax and cat.upper() == "VINO":
            cls.tax_19_vino += round(float(value))
            cls.ipo_19_vino += round(float(ipo))

        elif 19 == tax and cat.upper() == "CIGARRILLO":
            cls.tax_19_cigarrillo += round(float(value))
            cls.ipo_19_cigarrillo += round(float(ipo))

        elif 19 == tax and cat == "BOLSA":
            cls.tax_19_bolsa += round(float(value))

    @staticmethod
    def Tax_General(cls, number,date, client):
        if int(cls.tax_19_general) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 24080501,
                'accounting_account': "IVA VTA GNERAL 19%",
                'identification':client,
                'description':"IVA VTA GNERAL 19%",
                'debit':0,
                'credit':cls.tax_19_general
            })
        if int(cls.tax_5_general) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 24080502,
                'accounting_account': "IVA VTA GNERAL 5%",
                'identification':client,
                'description':"VA VTA GNERAL 5%",
                'debit':0,
                'credit':cls.tax_5_general
            })
        if int(cls.ipo_0_general) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 14300115,
                'accounting_account': "IMPOCO VTA GENERAL",
                'identification':client,
                'description':"IMPOCO VTA GENERAL",
                'debit':0,
                'credit':cls.ipo_0_general
            })

    @staticmethod
    def Licor(cls,number,date,client):
        if int(cls.tax_19_licor) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 24080505,
                'accounting_account': "IVA VTA LICOR 5",
                'identification':client,
                'description':"IVA VTA LICOR 5 ",
                'debit':0,
                'credit':cls.tax_19_licor
            })
        if int(cls.ipo_19_licor) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 14300116,
                'accounting_account': "IMPOCO VTA LICOR GNERAL",
                'identification':client,
                'description':"IMPOCO VTA LICOR GNERAL",
                'debit':0,
                'credit':cls.ipo_19_licor
            })

    @staticmethod    
    def Cerveza(cls,number,date,client):
        if int(cls.tax_19_cerveza) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 24080507,
                'accounting_account': "IVA VTA CERVEZA",
                'identification':client,
                'description':"IVA VTA CERVEZA",
                'debit':0,
                'credit':cls.tax_19_cerveza
            })
        if int(cls.ipo_19_cerveza) > 0:
            cls.data.append({
                'Secuencia':number,
                'Fecha elaboración': date,
                'Código contable': 14300117,
                'Cuenta contable': "IMPOCON VTA CERVEZA",
                'Identificación':client,
                'Descripción':"IMPOCON VTA CERVEZA",
                'Débito':0,
                'Crédito':cls.ipo_19_cerveza
            })

    @staticmethod
    def Vino(cls,number,date,client):
        if int(cls.tax_19_vino) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 24080509,
                'accounting_account': "IVA VTA VINO",
                'identification':client,
                'description':"IVA VTA VINO",
                'debit':0,
                'credit':cls.tax_19_vino
            })
        if int(cls.ipo_19_vino) > 0:
            cls.data.append({
                'Secuencia':number,
                'Fecha elaboración': date,
                'Código contable': 14300118,
                'Cuenta contable': "IMPOCON VTA VINO",
                'Identificación':client,
                'Descripción':"IMPOCON VTA VINO",
                'Débito':0,
                'Crédito':cls.ipo_19_vino
            })

    @staticmethod
    def Cigarrillo(cls,number,date,client):
        if int(cls.tax_19_cigarrillo) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 24080511,
                'accounting_account': "IVA 19 VTA CIGARRILLO",
                'identification':client,
                'description':"IVA 19 VTA CIGARRILLO",
                'debit':0,
                'credit':cls.tax_19_cigarrillo
            })
        if int(cls.ipo_19_cigarrillo) > 0:
            cls.data.append({
                'Secuencia':number,
                'Fecha elaboración': date,
                'Código contable': 14300119,
                'Cuenta contable': "IMPO VTA CIGARRILLO",
                'Identificación':client,
                'Descripción':"IMPO VTA CIGARRILLO",
                'Débito':0,
                'Crédito':cls.ipo_19_cigarrillo
            })

    @staticmethod
    def Gaseosa(cls,number,date,client):
        if int(cls.tax_19_gaseosa) > 0:
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 24080513,
                'accounting_account': "IVA GASEOSA",
                'identification':client,
                'description':"IVA GASEOSA",
                'debit':0,
                'credit':cls.tax_19_gaseosa
            })


    @staticmethod
    def segment_months(start, end):
        current_date = start
        end_date = end
        segments = []
        
        while current_date <= end_date:
            next_month = current_date.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)

            if last_day > end_date:
                last_day = end_date
            segments.append((current_date, last_day))
            current_date = last_day + timedelta(days=1)
        return segments

   
    @classmethod
    def generate_accounting(cls, data):
        result = False
        message = []
        try:
            invoice = Invoice.objects.prefetch_related('details_invoice_set').get(
                pk=data['pk_invoice'],
                branch=data['pk_branch']
            )
            cls.Taxes(cls)
            cls.Name_Category_Data(cls)
            # for invoice in invoices_queryset:
            total = 0
            number = invoice.number
            date = invoice.date
            client = invoice.customer.identification_number

            for detail in invoice.details_invoice_set.all():
                product = Product.objects.get(pk=detail.identification)
                cat = product.subcategory.category.name.upper()
                tax = detail.tax_value
                quantity = detail.quantity
                base = detail.price * quantity
                ipo = detail.ipo * quantity
                value_tax = detail.tax

                cls.Name_Category(cls, cat, tax, number, client, base, date)
                cls.Calculate_Taxes(cls,ipo,tax,value_tax,cat)
                cls.Tax_General(cls,number,date,client)
                cls.Gaseosa(cls,number,date,client)
                cls.Licor(cls,number,date,client)
                cls.Cerveza(cls,number,date,client)
                cls.Vino(cls,number,date,client)
                cls.Cigarrillo(cls,number,date,client)
                cls.Taxes(cls)
                total += base + value_tax + ipo
            cls.data.append({
                'sequence':number,
                'date_created': date,
                'accounting_code': 11050505,
                'accounting_account': f"Caja General {invoice.branch.name}",
                'identification':client,
                'description': f"Caja General {invoice.branch.name}",
                'debit': total,
                'credit':0
            })
            _result = cls.create_accountingentry(cls.data, invoice)
            if _result['result']:
                cls.data = []
                result = True
        except Exception as e:
            message = str(e)
            print(e,'ERROR generate_accounting')
        return {'result': result, 'message': message, 'data':cls.data}


        
    @classmethod
    def generate_excel(cls, data):
        result = False
        message = None
        date_from_str = str(data.get('date_from'))
        date_to_str = str(data.get('date_to'))
        list_document = []

        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d')
            if date_to < date_from:
                raise ValueError("The date 'date_to' cannot be earlier than 'date_from'.")
        except ValueError as e:
            raise ValueError("Dates must be in the format 'YYYY-MM-DD' and be valid.") from e
        months = cls.segment_months(date_from, date_to)
        documentation_dir = "/deploy/api/media"
        cls.delete_files_with_71(documentation_dir, data['pk_branch'],True)
        for i, (start, end) in enumerate(months, 1):
            if isinstance(start, datetime):
                month = start.month
            else:
                month = datetime.strptime(start, "%Y-%m-%d %H:%M:%S").month

            list_month = {
                1: "Enero",
                2: "Febrero",
                3: "Marzo",
                4: "Abril",
                5: "Mayo",
                6: "Junio",
                7: "Julio",
                8: "Agosto",
                9: "Septiembre",
                10: "Octubre",
                11: "Noviembre",
                12: "Diciembre"
            }
            month = list_month[month]
            invoices_queryset = cls.objects.filter(
                invoice__date__range=(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')),
                invoice__branch=data['pk_branch']
            )
            wb = Workbook()
            ws = wb.active
            ws.title = "Asiento Contable"
            headers = ['Secuencia', 'Fecha elaboración', 'Código contable', 
                       'Cuenta contable', 'Identificación', 'Descripción', 
                       'Débito', 'Crédito']
            ws.append(headers)
            try:
                for entry in invoices_queryset:
                    ws.append([
                        int(entry.sequence),
                        str(entry.date_created),
                        str(entry.accounting_code),
                        str(entry.accounting_account),
                        int(entry.identification),
                        entry.description,
                        round(entry.debit),
                        round(entry.credit),
                    ])
                _path = os.path.dirname(Path(__file__).resolve())
                file_ = f'asiento_contable_{month}_{data["pk_branch"]}.xlsx'
                file_path = os.path.join(documentation_dir,file_)
                url_xlsx = f"{env.URL_LOCAL}/media/{file_}"
                list_document.append(url_xlsx)
                wb.save(file_path.replace('\\','/'))
                result = True
                message = "El archivo Excel se ha creado y guardado exitosamente."
                url_excel = f"{env.URL_LOCAL}/"
            except Exception as ex_xlsx:
                print(ex_xlsx)
                message = str(ex_xlsx)
        if len(list_document) > 1:
            branch = data["pk_branch"]
            cls.compress_files_with_71(documentation_dir, f"compressed_files_{branch}.zip", branch)
            cls.delete_files_with_71(documentation_dir,branch,False)
            list_document = [f"{env.URL_LOCAL}/media/compressed_files_{branch}.zip"]
        return {'result': result, 'message': message,'document':list_document}

    @staticmethod
    def delete_files_with_71(path,branch,_zip):
        files = glob.glob(os.path.join(path, f'*{branch}.xlsx'))
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
                print(f"File deleted: {file}")
            else:
                print(f"The file does not exist: {file}")
        if _zip:
            zip_file = os.path.join(path, f'compressed_files_{branch}.zip')
            if os.path.isfile(zip_file):
                os.remove(zip_file)
                print(f"Compressed file deleted: {zip_file}")
            else:
                print(f"The compressed file does not exist: {zip_file}")
        print("File deletion process completed.")

    @staticmethod
    def compress_files_with_71(path, zip_name, branch):
        files = glob.glob(os.path.join(path, f'*{branch}.xlsx'))
        if files:
            with zipfile.ZipFile(f"{path}/{zip_name}", 'w') as zipf:
                for file in files:
                    if os.path.isfile(file):
                        zipf.write(file, os.path.basename(file))
                        print(f"File added to ZIP: {file}")
            print(f"Compression completed. ZIP file created: {zip_name}")
        else:
            print("No files found to compress.")