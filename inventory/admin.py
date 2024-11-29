from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_filter = ('branch__name',)
    list_display = ['code','name','quantity','quantity_unit','bale_quantity', 'price_1','price_2','price_3',]
    search_fields = ['code','branch__name','name']

class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('branch__name',)
    list_display = ['id','name',]
    search_fields = ['name']

admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory)
admin.site.register(Product,ProductAdmin)
admin.site.register(History_Product)
admin.site.register(Supplier)
admin.site.register(Product_Reserved)
admin.site.register(Best_Selling_Product)