from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from .models import Product, Customer, Order, OrderItem, ShippingAddress
import uuid
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# ¡Importaciones clave para el correo!
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from django.http import JsonResponse
import json

from django.contrib.auth import logout as auth_logout
from django.db.models import Q
# ================================================================
# ===============  FUNCIONES AUXILIARES DE CARRITO   =============
# ================================================================

# ... (el resto de tus funciones auxiliares _get_cart, _recount, _build_cart no cambian) ...
def _get_cart(session):
    """Obtiene o crea el carrito dentro de la sesión."""
    return session.setdefault("cart", {})

def _recount(session):
    """Recalcula el total de artículos y actualiza la sesión."""
    cart = _get_cart(session)
    session["cart_count"] = sum(int(q) for q in cart.values())
    session.modified = True

def _build_cart(session):
    """Convierte el carrito de la sesión en un contexto listo para la plantilla."""
    cart = _get_cart(session)
    if not cart:
        return {"items": [], "total": 0, "count": 0}

    ids = [int(pid) for pid in cart.keys()]
    products = {p.id: p for p in Product.objects.filter(id__in=ids)}

    items, total, count = [], 0, 0
    for pid, qty in cart.items():
        pid_int = int(pid)
        if pid_int not in products:
            continue
        p = products[pid_int]
        qty = max(1, int(qty))
        price = float(p.price)
        sub = round(price * qty, 2)
        items.append({"product": p, "quantity": qty, "subtotal": sub})
        total += sub
        count += qty

    session["cart_count"] = count
    session.modified = True
    return {"items": items, "total": round(total, 2), "count": count}

# ================================================================
# ====================  VISTAS PRINCIPALES   =====================
# ================================================================

# ... (tus vistas store, cart, checkout no cambian) ...
# def store(request):
#    """Página principal: muestra los productos disponibles."""
#    products = Product.objects.all().order_by("name")
#    ctx = {
#        "products": products,
#        "cart_count": request.session.get("cart_count", 0),
#    }
#    return render(request, "generales/store.html", ctx)

def store(request):
    """Página principal: muestra los productos disponibles."""
    # CAMBIO: Ahora solo filtramos productos con stock mayor a 0
    products = Product.objects.filter(stock__gt=0).order_by("name") 
    ctx = {
        "products": products,
        "cart_count": request.session.get("cart_count", 0),
    }
    return render(request, "generales/store.html", ctx)

def cart(request):
    """Muestra el contenido actual del carrito."""
    cart_ctx = _build_cart(request.session)
    return render(request, "generales/cart.html", {
        "cart": cart_ctx,
        "cart_count": cart_ctx["count"]
    })

def checkout(request):
    """Página de checkout (requiere login para comprar)."""
    cart_ctx = _build_cart(request.session)
    return render(request, "generales/checkout.html", {
        "cart": cart_ctx,
        "cart_count": cart_ctx["count"]
    })

# ================================================================
# ==================  FUNCIONES DEL CARRITO   ===================
# ================================================================

# ... (tus funciones de carrito add_to_cart, update_cart, etc., no cambian) ...
# ... (tus importaciones y otras vistas van aquí arriba) ...
# ... (_get_cart, _recount, _build_cart, store, cart, checkout, etc.) ...

# ================================================================
# ==================  FUNCIONES DEL CARRITO (MODIFICADAS) ========
# ================================================================

@require_POST
def add_to_cart(request, product_id):
    """Agrega un producto al carrito de sesión (CON CONTROL DE STOCK)."""
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("qty", 1))
    qty = max(1, qty) # Asegurarse de que sea al menos 1

    cart = _get_cart(request.session)
    
    # --- VALIDACIÓN DE STOCK ---
    qty_in_cart = cart.get(str(product_id), 0)
    new_total_qty = qty_in_cart + qty
    
    if new_total_qty > product.stock:
        # Si se pide más de lo que hay, no se agrega.
        message = f"¡Stock insuficiente! Solo quedan {product.stock} de '{product.name}'. Ya tienes {qty_in_cart} en tu carrito."
        
        # Respuesta para AJAX (si esta función se usa para eso)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': message,
                'cart_count': request.session.get("cart_count", 0)
            })
        
        # Respuesta para formulario normal
        messages.error(request, message)
        return redirect("cart")
    # --- FIN DE VALIDACIÓN ---

    # Si hay stock, se procede como antes
    cart[str(product_id)] = new_total_qty # Se usa la nueva cantidad total
    request.session["cart"] = cart
    _recount(request.session)

    # Respuesta para AJAX (si esta función se usa para eso)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_ctx = _build_cart(request.session)
        return JsonResponse({
            'success': True,
            'message': f"Se agregó '{product.name}' x{qty} al carrito.",
            'cart_count': cart_ctx['count'],
            'product_name': product.name
        })

    # Respuesta para formulario normal
    messages.success(request, f"Se agregó '{product.name}' x{qty} al carrito.")
    return redirect("cart")

@require_POST
def add_to_cart_ajax(request, product_id):
    """Versión AJAX para agregar productos (CON CONTROL DE STOCK)."""
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("qty", 1))
    qty = max(1, qty) # Asegurarse de que sea al menos 1

    cart = _get_cart(request.session)

    # --- VALIDACIÓN DE STOCK ---
    qty_in_cart = cart.get(str(product_id), 0)
    new_total_qty = qty_in_cart + qty
    
    if new_total_qty > product.stock:
        # No hay suficiente stock, devolver error
        return JsonResponse({
            'success': False,
            'message': f"¡Stock insuficiente! Solo quedan {product.stock} de '{product.name}'. Ya tienes {qty_in_cart} en tu carrito.",
            'cart_count': request.session.get("cart_count", 0)
        })
    # --- FIN DE VALIDACIÓN ---

    # Si hay stock, se procede como antes
    cart[str(product_id)] = new_total_qty
    request.session["cart"] = cart
    _recount(request.session)

    cart_ctx = _build_cart(request.session)
    return JsonResponse({
        'success': True,
        'message': f"Se agregó '{product.name}' x{qty} al carrito.",
        'cart_count': cart_ctx['count'],
        'product_name': product.name
    })

# ... (el resto de tus vistas: update_cart, remove_from_cart, etc.) ...
# ... (process_order, custom_logout, register, profile, etc.) ...



@require_POST
def update_cart(request):
    """Actualiza las cantidades de productos en el carrito."""
    cart = _get_cart(request.session)
    for key, value in request.POST.items():
        if not key.startswith("qty_"):
            continue
        pid = key.split("_", 1)[1]
        try:
            qty = int(value)
        except ValueError:
            qty = 0
        if qty <= 0:
            cart.pop(pid, None)
        else:
            cart[pid] = qty
    request.session["cart"] = cart
    _recount(request.session)
    messages.info(request, "Cantidades actualizadas.")
    return redirect("cart")

def remove_from_cart(request, product_id):
    """Elimina un producto específico del carrito."""
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    _recount(request.session)
    messages.info(request, "Producto eliminado del carrito.")
    return redirect("cart")
# ================================================================
# =====================  PROCESAR PEDIDO   ======================
# ================================================================

@require_POST
def process_order(request):
    """Crea una orden en la base de datos y envía un correo HTML."""
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para completar la compra.")
        return redirect("login")

    cart_ctx = _build_cart(request.session)
    if cart_ctx["count"] == 0:
        messages.info(request, "Tu carrito está vacío.")
        return redirect("store")

    try:
        # 1️⃣ Crear o identificar al cliente
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={
                "name": f"{request.POST.get('first_name', '')} {request.POST.get('last_name', '')}".strip() or request.user.username,
                "email": request.POST.get('email', request.user.email),
            },
        )

        # 2️⃣ Crear la orden
        order = Order.objects.create(
            customer=customer,
            complete=True,
            transaction_id=uuid.uuid4().hex[:12]
        )

        # 3️⃣ Agregar los items del carrito a la orden
        for it in cart_ctx["items"]:
            OrderItem.objects.create(
                order=order,
                product=it["product"],
                quantity=it["quantity"]
            )
            if hasattr(it["product"], "stock"):
                it["product"].stock = max(0, it["product"].stock - it["quantity"])
                it["product"].save(update_fields=["stock"])

        # 4️⃣ Guardar dirección de envío
        shipping_address = ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=request.POST.get("address", ""),
            city=request.POST.get("city", ""),
            state=request.POST.get("state", "Guatemala"),
            zipcode=request.POST.get("zip", ""),
        )

        # 5️⃣ Limpiar el carrito
        request.session["cart"] = {}
        request.session["cart_count"] = 0
        request.session.modified = True

        # 6️⃣ ENVIAR CORREO DE CONFIRMACIÓN (VERSIÓN MEJORADA)
        if customer.email and customer.email.strip() != '':
            try:
                email_subject = f'✅ Confirmación de Pedido #{order.id} - Zapatería'
                
                # Preparamos el contexto para la plantilla HTML
                context = {
                    'user': request.user,
                    'order': order,
                    'cart': cart_ctx,
                    'shipping_address': shipping_address,
                    'customer': customer,
                    'phone': request.POST.get('phone', 'No proporcionado')
                }
                
                # Renderizamos el HTML y el texto plano
                html_message = render_to_string('emails/confirmacion_pedido.html', context)
                plain_message = render_to_string('emails/confirmacion_pedido.txt', context)

                print("=" * 60)
                print("🛍️  ENVIANDO CORREO DE CONFIRMACIÓN (HTML)...")
                print(f"📧 Para: {customer.email}")
                print(f"📦 Pedido: #{order.id}")
                print("=" * 60)
                
                send_mail(
                    email_subject,
                    plain_message, # Fallback de texto plano
                    settings.DEFAULT_FROM_EMAIL,
                    [customer.email],
                    html_message=html_message, # Contenido principal en HTML
                    fail_silently=False,
                )
                
                print("✅ CORREO DE CONFIRMACIÓN ENVIADO EXITOSAMENTE")
                
            except Exception as e:
                print(f"❌ ERROR ENVIANDO CORREO DE CONFIRMACIÓN: {str(e)}")
        else:
            print(f"⚠️  PEDIDO #{order.id} PROCESADO, PERO EL CLIENTE NO TIENE EMAIL. NO SE ENVÍA CORREO.")


        messages.success(request, f"¡Pedido #{order.id} confirmado exitosamente! Revisa tu correo para ver los detalles.")
        return redirect("store")

    except Exception as e:
        messages.error(request, f"Error al procesar el pedido: {str(e)}")
        print(f"ERROR GRAVE EN PROCESS_ORDER: {str(e)}")
        return redirect("checkout")
    
# ... (el resto de tus vistas custom_logout, register, etc., no cambian) ...
def custom_logout(request):
    """Vista personalizada para cerrar sesión"""
    auth_logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('store')

def product_detail(request, product_id):
    """Vista básica para mostrar detalles de producto (opcional)."""
    product = get_object_or_404(Product, id=product_id)
    return HttpResponse(f"Detalles del producto: {product.name}")

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido")
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mensajes de ayuda más claros
        self.fields['password1'].help_text = '''
        <ul class="password-help">
            <li>Mínimo 16 caracteres</li>
            <li>Al menos 1 letra mayúscula</li>
            <li>Al menos 1 número</li>
            <li>Al menos 1 símbolo especial</li>
        </ul>
        '''

def register(request):
    """Registro de usuarios con validaciones personalizadas."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            
            user.email = request.POST.get('email', '') 
            
            user.is_staff = False
            user.is_superuser = False
            user.save() 
            
            if user.email:
                try:
                    # --- ESTA ES LA PARTE ACTUALIZADA ---
                    # Cambia el print para saber que es la versión HTML
                    print("=" * 50)
                    print("🚀 INTENTANDO ENVIAR CORREO HTML DE BIENVENIDA...")
                    print(f"📧 Para: {user.email}")
                    print("=" * 50)
                    
                    email_subject = '¡Bienvenido/a a GearKicks! 🛍️'
                    context = {'user': user}
                    
                    # Renderiza las dos plantillas que creamos
                    html_message = render_to_string('emails/bienvenida.html', context)
                    plain_message = render_to_string('emails/bienvenida.txt', context)

                    send_mail(
                        email_subject,
                        plain_message, # Fallback de texto plano
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message, # Contenido principal en HTML
                        fail_silently=False,
                    )
                    # --- FIN DE LA PARTE ACTUALIZADA ---
                    
                    print("✅ CORREO ENVIADO EXITOSAMENTE")
                    messages.success(request, "✅ Cuenta creada y correo de confirmación enviado.")
                    
                except Exception as e:
                    print(f"❌ ERROR ENVIANDO CORREO: {str(e)}")
                    messages.success(request, "✅ Cuenta creada (pero no se pudo enviar el correo).")
            else:
                print("⚠️  Usuario sin email, no se envía correo")
                messages.success(request, "✅ Cuenta creada exitosamente.")
            
            auth_login(request, user)
            return redirect("store")
    else:
        form = CustomUserCreationForm()
    
    return render(request, "registration/register.html", {"form": form})

# ================================================================
# =====================  PERFIL DE USUARIO   =====================
# ================================================================

@login_required
def profile(request):
    """Vista del perfil del usuario con acceso al menú de gerente."""
    is_gerente = request.user.groups.filter(name='Gerente').exists()

    # Obtener las órdenes del usuario si es cliente
    customer = None
    orders = []
    if hasattr(request.user, 'customer'):
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_order')

    context = {
        'is_gerente': is_gerente,
        'customer': customer,
        'orders': orders,
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "generales/profile.html", context)

# ================================================================
# ====================  MENÚ DE GERENTE   ========================
# ================================================================

@login_required
@permission_required('app.view_product', raise_exception=True)
def gerente_dashboard(request):
    """Dashboard principal del gerente."""
    # Verificar que sea gerente
    if not request.user.groups.filter(name='Gerente').exists() and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('profile')

    # Estadísticas
    total_products = Product.objects.count()
    total_orders = Order.objects.filter(complete=True).count()
    pending_orders = Order.objects.filter(complete=False).count()
    low_stock = Product.objects.filter(stock__lt=5).count()

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'low_stock': low_stock,
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "gerente/dashboard.html", context)

# ================================================================
# ==================  GESTIÓN DE PRODUCTOS   =====================
# ================================================================

@login_required
@permission_required('app.view_product', raise_exception=True)
def gerente_products_list(request):
    """Lista de productos con búsqueda y filtros."""
    # Verificar que sea gerente
    if not request.user.groups.filter(name='Gerente').exists() and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('profile')

    query = request.GET.get('q', '')
    products = Product.objects.all().order_by('name')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(size__icontains=query)
        )

    context = {
        'products': products,
        'query': query,
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "gerente/products_list.html", context)

@login_required
@permission_required('app.add_product', raise_exception=True)
def gerente_product_add(request):
    """Agregar nuevo producto."""
    if request.method == 'POST':
        try:
            product = Product.objects.create(
                name=request.POST.get('name'),
                brand=request.POST.get('brand', ''),
                size=request.POST.get('size', ''),
                price=float(request.POST.get('price')),
                stock=int(request.POST.get('stock', 0)),
                image_url=request.POST.get('image_url', ''),
                digital=request.POST.get('digital') == 'on'
            )
            messages.success(request, f"Producto '{product.name}' agregado exitosamente.")
            return redirect('gerente_products_list')
        except Exception as e:
            messages.error(request, f"Error al agregar producto: {str(e)}")

    context = {
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "gerente/product_form.html", context)

@login_required
@permission_required('app.change_product', raise_exception=True)
def gerente_product_edit(request, product_id):
    """Editar producto existente."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.brand = request.POST.get('brand', '')
            product.size = request.POST.get('size', '')
            product.price = float(request.POST.get('price'))
            product.stock = int(request.POST.get('stock', 0))
            product.image_url = request.POST.get('image_url', '')
            product.digital = request.POST.get('digital') == 'on'
            product.save()

            messages.success(request, f"Producto '{product.name}' actualizado exitosamente.")
            return redirect('gerente_products_list')
        except Exception as e:
            messages.error(request, f"Error al actualizar producto: {str(e)}")

    context = {
        'product': product,
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "gerente/product_form.html", context)

@login_required
@permission_required('app.delete_product', raise_exception=True)
def gerente_product_delete(request, product_id):
    """Eliminar producto."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f"Producto '{product_name}' eliminado exitosamente.")
        return redirect('gerente_products_list')

    context = {
        'product': product,
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "gerente/product_confirm_delete.html", context)

# ================================================================
# ==================  GESTIÓN DE ÓRDENES   =======================
# ================================================================

@login_required
@permission_required('app.view_order', raise_exception=True)
def gerente_orders_list(request):
    """Lista de órdenes con filtros."""
    # Verificar que sea gerente
    if not request.user.groups.filter(name='Gerente').exists() and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('profile')

    status = request.GET.get('status', '')
    query = request.GET.get('q', '')

    orders = Order.objects.all().order_by('-date_order')

    if status == 'complete':
        orders = orders.filter(complete=True)
    elif status == 'pending':
        orders = orders.filter(complete=False)

    if query:
        orders = orders.filter(
            Q(transaction_id__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(customer__email__icontains=query)
        )

    context = {
        'orders': orders,
        'status': status,
        'query': query,
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "gerente/orders_list.html", context)

@login_required
@permission_required('app.view_order', raise_exception=True)
def gerente_order_detail(request, order_id):
    """Ver detalle de una orden."""
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    shipping = ShippingAddress.objects.filter(order=order).first()

    # Calcular total
    total = sum(item.quantity * item.product.price for item in order_items if item.product)

    context = {
        'order': order,
        'order_items': order_items,
        'shipping': shipping,
        'total': total,
        'cart_count': request.session.get("cart_count", 0),
    }
    return render(request, "gerente/order_detail.html", context)

@login_required
@permission_required('app.change_order', raise_exception=True)
def gerente_order_update_status(request, order_id):
    """Actualizar estado de una orden."""
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status') == 'complete'
        order.complete = new_status
        order.save()

        status_text = "completada" if new_status else "pendiente"
        messages.success(request, f"Orden #{order.id} marcada como {status_text}.")
        return redirect('gerente_order_detail', order_id=order.id)

    return redirect('gerente_orders_list')

