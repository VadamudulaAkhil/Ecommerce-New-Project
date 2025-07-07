from django.contrib import admin
from .models import *


admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Payment_Order)
# admin.site.register(Electronics)
# admin.site.register(Mobiles)
# admin.site.register(Accessories)
# admin.site.register(Home_Appliances)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'digital', 'category']
    list_filter = ['digital', 'category']

