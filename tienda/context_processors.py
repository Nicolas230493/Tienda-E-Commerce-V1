def cart_context(request):
    carrito = request.session.get('carrito', {})
    cart_count = sum(carrito.values())
    return {
        'cart_count': cart_count
    }
