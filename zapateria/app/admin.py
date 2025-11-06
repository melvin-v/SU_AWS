from django.contrib import admin
from .models import *

# ====== Configuración del sitio admin ======
admin.site.site_header = "Zapatería - Panel de Administración"
admin.site.site_title = "Zapatería Admin"
admin.site.index_title = "Bienvenido al Panel de Control"

# ====== Configuración de modelos ======
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "brand", "size", "price", "stock")
    list_editable = ("price", "stock")
    search_fields = ("name", "brand", "size")
    list_filter = ("brand", "size")
    list_per_page = 20

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "email")
    search_fields = ("name", "email", "user__username")
    list_per_page = 20

class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "date_order", "complete", "transaction_id")
    list_filter = ("complete", "date_order")
    search_fields = ("customer__name", "transaction_id")
    date_hierarchy = "date_order"
    list_per_page = 20

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "order", "quantity", "date_added")
    list_filter = ("date_added",)
    search_fields = ("product__name", "order__transaction_id")
    list_per_page = 20

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "order", "address", "city", "state", "zipcode")
    search_fields = ("customer__name", "address", "city", "state")
    list_filter = ("state", "city")
    list_per_page = 20

# ====== Registro de modelos ======
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Product, ProductAdmin)