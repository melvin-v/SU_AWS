# Menú de Gerente - Zapatería

## Descripción

Se ha implementado un sistema completo de gestión de gerente con permisos intermedios entre usuario normal y superusuario. Los gerentes pueden acceder a funcionalidades administrativas desde su perfil de usuario.

## Características Implementadas

### 1. Grupo de Gerente con Permisos Específicos
- **Productos**: Ver, agregar, modificar y eliminar
- **Órdenes**: Ver y modificar estado (NO puede crear ni eliminar órdenes)
- **OrderItems**: Ver y modificar

### 2. Acceso desde el Perfil de Usuario
- Se agregó botón "Mi Perfil" en el menú de navegación
- El perfil muestra opciones según el rol del usuario:
  - **Clientes**: Ven su historial de pedidos
  - **Gerentes**: Ven acceso al panel de gerente + historial
  - **Superusuarios**: Acceso completo a admin + panel de gerente

### 3. Panel de Gerente
Incluye las siguientes secciones:

#### Dashboard (`/gerente/`)
- Estadísticas generales:
  - Total de productos
  - Órdenes completadas
  - Órdenes pendientes
  - Productos con stock bajo (menos de 5 unidades)
- Accesos rápidos a todas las funciones

#### Gestión de Productos (`/gerente/productos/`)
- **Listar productos**: Con búsqueda por nombre, marca o talla
- **Agregar productos**: Formulario completo con validación
- **Editar productos**: Modificar todos los campos
- **Eliminar productos**: Con confirmación de seguridad

#### Gestión de Órdenes (`/gerente/ordenes/`)
- **Listar órdenes**: Con filtros por estado y búsqueda
- **Ver detalles**: Información completa de la orden
  - Datos del cliente
  - Dirección de envío
  - Items pedidos con precios
  - Total calculado
- **Cambiar estado**: Marcar como completada o pendiente

## Instalación y Configuración

### 1. Crear el Grupo de Gerente

Ejecuta el siguiente comando para configurar el grupo con los permisos:

```bash
python manage.py setup_gerente
```

Este comando:
- Crea el grupo "Gerente"
- Asigna permisos específicos para productos y órdenes
- Muestra confirmación de la configuración

### 2. Asignar Usuarios al Grupo Gerente

Para convertir a un usuario en gerente:

```bash
python manage.py assign_gerente nombre_usuario
```

Este comando:
- Agrega al usuario al grupo "Gerente"
- Le da permiso `is_staff=True` para acceder al panel
- Confirma la asignación de permisos

**Ejemplo:**
```bash
python manage.py assign_gerente juan
```

### 3. Verificar la Instalación

1. Inicia sesión con un usuario gerente
2. Verás el botón "Mi Perfil" en el menú superior
3. En tu perfil, deberías ver el panel azul con acceso al Dashboard de Gerente

## Estructura de Archivos Creados/Modificados

### Archivos Nuevos:
```
app/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── setup_gerente.py        # Comando para configurar grupo
│       └── assign_gerente.py       # Comando para asignar usuarios
├── templates/
│   ├── generales/
│   │   └── profile.html            # Vista de perfil de usuario
│   └── gerente/
│       ├── dashboard.html          # Dashboard principal
│       ├── products_list.html      # Lista de productos
│       ├── product_form.html       # Formulario agregar/editar
│       ├── product_confirm_delete.html  # Confirmación eliminación
│       ├── orders_list.html        # Lista de órdenes
│       └── order_detail.html       # Detalle de orden
```

### Archivos Modificados:
```
app/
├── views.py                         # +10 vistas nuevas
├── urls.py                          # +11 rutas nuevas
└── templates/generales/main.html    # Botón "Mi Perfil" agregado
```

## URLs Disponibles

### Perfil
- `/profile/` - Perfil del usuario (requiere login)

### Panel de Gerente (requiere permisos)
- `/gerente/` - Dashboard principal
- `/gerente/productos/` - Lista de productos
- `/gerente/productos/agregar/` - Agregar producto
- `/gerente/productos/<id>/editar/` - Editar producto
- `/gerente/productos/<id>/eliminar/` - Eliminar producto
- `/gerente/ordenes/` - Lista de órdenes
- `/gerente/ordenes/<id>/` - Detalle de orden
- `/gerente/ordenes/<id>/actualizar/` - Cambiar estado

## Permisos y Seguridad

### Decoradores Implementados
- `@login_required` - Requiere autenticación
- `@permission_required` - Verifica permisos específicos
- Verificación adicional de grupo "Gerente" en vistas sensibles

### Diferencias con Superusuario

| Función | Gerente | Superusuario |
|---------|---------|--------------|
| Ver productos | ✅ | ✅ |
| Agregar productos | ✅ | ✅ |
| Modificar productos | ✅ | ✅ |
| Eliminar productos | ✅ | ✅ |
| Ver órdenes | ✅ | ✅ |
| Modificar estado órdenes | ✅ | ✅ |
| Crear órdenes manualmente | ❌ | ✅ |
| Eliminar órdenes | ❌ | ✅ |
| Acceso a Django Admin | ❌ | ✅ |
| Gestionar usuarios | ❌ | ✅ |
| Cambiar permisos | ❌ | ✅ |

## Funcionalidades Preservadas

✅ **Todas las funcionalidades existentes se mantienen intactas:**
- Sistema de carrito de compras
- Proceso de checkout
- Envío de correos de confirmación
- Registro y autenticación de usuarios
- Panel de administración de Jazzmin (solo superusuario)
- Todas las vistas públicas (tienda, carrito, etc.)

## Uso Diario

### Para Gerentes:

1. **Iniciar sesión** con tu cuenta de gerente
2. **Ir a "Mi Perfil"** desde el menú superior
3. **Acceder al Dashboard** para ver estadísticas
4. **Gestionar productos:**
   - Usar el buscador para encontrar productos
   - Agregar nuevos productos desde el botón verde
   - Editar o eliminar productos existentes
5. **Gestionar órdenes:**
   - Filtrar por estado (completadas/pendientes)
   - Ver detalles completos de cada orden
   - Cambiar estado de órdenes según sea necesario

### Para Administradores:

Para crear un nuevo gerente:
```bash
# 1. Si el usuario no existe, créalo desde Django Admin
# 2. Asigna el rol de gerente:
python manage.py assign_gerente nombre_usuario
```

## Notas Importantes

- Los gerentes tienen `is_staff=True` pero NO son superusuarios
- No pueden acceder al panel de Django Admin (solo superusuarios)
- No pueden eliminar órdenes (solo modificar su estado)
- El sistema verifica permisos en cada acción
- Todas las acciones están protegidas contra acceso no autorizado

## Soporte

Si encuentras algún problema:
1. Verifica que el comando `setup_gerente` se ejecutó correctamente
2. Confirma que el usuario tiene el grupo "Gerente" asignado
3. Revisa que el usuario tenga `is_staff=True`
4. Verifica los logs de Django para errores de permisos
