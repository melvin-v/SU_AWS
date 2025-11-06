from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Asigna un usuario al grupo Gerente'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario')

    def handle(self, *args, **kwargs):
        username = kwargs['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ Usuario "{username}" no existe'))
            return

        try:
            gerente_group = Group.objects.get(name='Gerente')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Grupo "Gerente" no existe'))
            self.stdout.write(self.style.WARNING('→ Ejecuta primero: python manage.py setup_gerente'))
            return

        # Agregar al grupo
        user.groups.add(gerente_group)

        # Dar permiso de staff (para acceder al área de gerente)
        if not user.is_staff:
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario "{username}" ahora tiene acceso al panel'))

        self.stdout.write(self.style.SUCCESS(f'✓ Usuario "{username}" agregado al grupo Gerente'))
        self.stdout.write(self.style.SUCCESS('  Permisos: gestión de productos y órdenes'))
