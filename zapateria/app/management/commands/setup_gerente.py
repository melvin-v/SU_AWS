from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from app.models import Product, Order, OrderItem

class Command(BaseCommand):
    help = 'Configura el grupo Gerente con permisos específicos'

    def handle(self, *args, **kwargs):
        # Crear o obtener el grupo Gerente
        gerente_group, created = Group.objects.get_or_create(name='Gerente')

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Gerente" creado'))
        else:
            self.stdout.write(self.style.WARNING('→ Grupo "Gerente" ya existía'))

        # Limpiar permisos existentes
        gerente_group.permissions.clear()

        # Obtener ContentTypes
        product_ct = ContentType.objects.get_for_model(Product)
        order_ct = ContentType.objects.get_for_model(Order)
        orderitem_ct = ContentType.objects.get_for_model(OrderItem)

        # Permisos para Productos (agregar, modificar, eliminar, ver)
        product_perms = Permission.objects.filter(
            content_type=product_ct,
            codename__in=['add_product', 'change_product', 'delete_product', 'view_product']
        )

        # Permisos para Órdenes (ver, modificar - no crear ni eliminar)
        order_perms = Permission.objects.filter(
            content_type=order_ct,
            codename__in=['view_order', 'change_order']
        )

        # Permisos para OrderItems (ver, modificar - no crear ni eliminar)
        orderitem_perms = Permission.objects.filter(
            content_type=orderitem_ct,
            codename__in=['view_orderitem', 'change_orderitem']
        )

        # Asignar todos los permisos al grupo
        all_perms = list(product_perms) + list(order_perms) + list(orderitem_perms)
        gerente_group.permissions.set(all_perms)

        self.stdout.write(self.style.SUCCESS(f'✓ Asignados {len(all_perms)} permisos al grupo Gerente'))
        self.stdout.write(self.style.SUCCESS('  - Productos: agregar, modificar, eliminar, ver'))
        self.stdout.write(self.style.SUCCESS('  - Órdenes: ver, modificar'))
        self.stdout.write(self.style.SUCCESS('  - Items de Orden: ver, modificar'))

        self.stdout.write(self.style.SUCCESS('\n✓ Configuración completada'))
        self.stdout.write(self.style.WARNING('\nPara asignar un usuario al grupo Gerente:'))
        self.stdout.write(self.style.WARNING('  python manage.py assign_gerente <username>'))
