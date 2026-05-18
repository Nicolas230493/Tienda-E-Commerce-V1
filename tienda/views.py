import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .models import Categoria, Producto, Newsletter, Pedido, Perfil, ItemPedido

def home(request):
    categoria_slug = request.GET.get('categoria')
    search_query = request.GET.get('q')
    
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()
    
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)
        
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains=search_query) | 
            Q(descripcion__icontains=search_query) |
            Q(marca__icontains=search_query)
        )

    context = {
        'categorias': categorias,
        'categorias_nav': categorias[:4],
        'productos': productos,
    }
    return render(request, 'home.html', context)

def producto_detalle(request, slug):
    producto = get_object_or_404(Producto, slug=slug)
    # Productos relacionados (misma categoría)
    relacionados = Producto.objects.filter(categoria=producto.categoria).exclude(id=producto.id)[:4]
    
    return render(request, 'producto_detalle.html', {
        'producto': producto,
        'relacionados': relacionados,
    })

# ── AUTENTICACIÓN ──

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def perfil(request):
    pedidos = request.user.pedidos.all()
    return render(request, 'perfil.html', {'pedidos': pedidos})

# ── VISTAS AJAX ──

def obtener_carrito(request):
    carrito_session = request.session.get('carrito', {})
    items = []
    subtotal = 0
    
    for product_id, cantidad in carrito_session.items():
        try:
            producto = Producto.objects.get(id=product_id)
            total_item = producto.precio * cantidad
            subtotal += total_item
            items.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'marca': producto.marca,
                'precio': str(producto.precio),
                'cantidad': cantidad,
                'total': str(total_item),
                'emoji': producto.emoji_preview,
                'imagen': producto.imagen.url if producto.imagen else None
            })
        except Producto.DoesNotExist:
            continue
    
    shipping = 0 if subtotal >= 99 or subtotal == 0 else 12
    total = subtotal + shipping
    
    return JsonResponse({
        'items': items,
        'subtotal': str(subtotal),
        'shipping': str(shipping),
        'total': str(total),
        'cart_count': sum(carrito_session.values())
    })

def agregar_al_carrito(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        producto = get_object_or_404(Producto, id=product_id)
        
        carrito = request.session.get('carrito', {})
        cantidad_actual = carrito.get(str(product_id), 0)
        
        if producto.stock <= cantidad_actual:
            return JsonResponse({'success': False, 'message': 'No hay más stock disponible'}, status=400)
            
        carrito[str(product_id)] = cantidad_actual + 1
        request.session['carrito'] = carrito
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(carrito.values()),
            'product_name': producto.nombre
        })
    return JsonResponse({'success': False}, status=400)

@login_required
def procesar_pedido(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        carrito_session = request.session.get('carrito', {})
        
        if not carrito_session:
            return JsonResponse({'success': False, 'message': 'El carrito está vacío'}, status=400)
            
        subtotal = 0
        items_a_crear = []
        
        for product_id, cantidad in carrito_session.items():
            producto = get_object_or_404(Producto, id=product_id)
            if producto.stock < cantidad:
                return JsonResponse({'success': False, 'message': f'Stock insuficiente para {producto.nombre}'}, status=400)
            
            subtotal += producto.precio * cantidad
            items_a_crear.append((producto, cantidad, producto.precio))
            
        shipping = 0 if subtotal >= 99 else 12
        total_pedido = subtotal + shipping
        
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total_pedido,
            nombre_completo=data.get('nombre_completo'),
            email=data.get('email'),
            direccion=data.get('direccion'),
            ciudad=data.get('ciudad'),
            zip_code=data.get('zip_code')
        )
        
        items_msg = ""
        for producto, cantidad, precio in items_a_crear:
            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                precio=precio,
                cantidad=cantidad
            )
            producto.stock -= cantidad
            producto.save()
            items_msg += f"- {cantidad}x {producto.nombre} (${precio})\n"
            
        # Enviar Email (Simulado en consola por ahora)
        try:
            send_mail(
                f'Confirmación de Pedido #{pedido.id} - Impulso Shop',
                f'Hola {pedido.nombre_completo},\n\nGracias por tu compra. Aquí tienes el resumen de tu pedido:\n\n{items_msg}\nTotal: ${pedido.total}\n\nEn breve te contactaremos para el envío.',
                settings.DEFAULT_FROM_EMAIL,
                [pedido.email],
                fail_silently=True,
            )
        except:
            pass

        # SIMULACIÓN MERCADOPAGO
        # En un entorno real, aquí usarías el SDK de MercadoPago:
        # preference_data = { "items": [...], "external_reference": str(pedido.id) }
        # preference_response = sdk.preference().create(preference_data)
        # payment_url = preference_response["response"]["init_point"]
        
        # Simulamos una URL de pago (esto se reemplazaría por la real del SDK)
        payment_url = f"https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=simulated_{pedido.id}"
        pedido.mercado_pago_id = f"simulated_{pedido.id}"
        pedido.save()

        # Vaciar carrito
        request.session['carrito'] = {}
        
        return JsonResponse({
            'success': True,
            'order_id': pedido.id,
            'payment_url': payment_url
        })
        
    return JsonResponse({'success': False}, status=400)

def suscribir_newsletter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('nombre')
        email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email requerido'})
            
        try:
            Newsletter.objects.create(nombre=nombre, email=email)
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False, 'message': 'Error en la suscripción'})
            
    return JsonResponse({'success': False}, status=400)
