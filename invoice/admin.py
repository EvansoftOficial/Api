from django.contrib import admin
from .models import *

class InvoiceAdmin(admin.ModelAdmin):
    list_filter = ('branch__name',)
    search_fields = ['number','branch__name',]

admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Details_Invoice)
admin.site.register(Payment_Forms)
admin.site.register(Pass)
admin.site.register(History_Invoice)
admin.site.register(History_Pass)
admin.site.register(Note_Credit_Product)
admin.site.register(Shipping_Control)
admin.site.register(Cash_Closings)
admin.site.register(PaymentMethod)