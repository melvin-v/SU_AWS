from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", views.store, name="store"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("update-cart/", views.update_cart, name="update_cart"),
    path("process-order/", views.process_order, name="process_order"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("register/", views.register, name="register"),
    path("logout/", views.custom_logout, name="logout"),
    path("add-ajax/<int:product_id>/", views.add_to_cart_ajax, name="add_to_cart_ajax"),

    # Perfil de usuario
    path("profile/", views.profile, name="profile"),

    # Menú de gerente
    path("gerente/", views.gerente_dashboard, name="gerente_dashboard"),

    # Gestión de productos
    path("gerente/productos/", views.gerente_products_list, name="gerente_products_list"),
    path("gerente/productos/agregar/", views.gerente_product_add, name="gerente_product_add"),
    path("gerente/productos/<int:product_id>/editar/", views.gerente_product_edit, name="gerente_product_edit"),
    path("gerente/productos/<int:product_id>/eliminar/", views.gerente_product_delete, name="gerente_product_delete"),

    # Gestión de órdenes
    path("gerente/ordenes/", views.gerente_orders_list, name="gerente_orders_list"),
    path("gerente/ordenes/<int:order_id>/", views.gerente_order_detail, name="gerente_order_detail"),
    path("gerente/ordenes/<int:order_id>/actualizar/", views.gerente_order_update_status, name="gerente_order_update_status"),
]
