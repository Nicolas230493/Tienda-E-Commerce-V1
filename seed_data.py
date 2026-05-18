import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tienda.models import Categoria, Producto

def populate():
    # Crear Categorías
    ropa = Categoria.objects.get_or_create(nombre='Ropa', emoji='👗', color_clase='cat1')[0]
    acc = Categoria.objects.get_or_create(nombre='Accesorios', emoji='👜', color_clase='cat2')[0]
    cal = Categoria.objects.get_or_create(nombre='Calzado', emoji='👟', color_clase='cat3')[0]
    hogar = Categoria.objects.get_or_create(nombre='Hogar', emoji='🏠', color_clase='cat4')[0]

    # Crear Productos
    productos_data = [
        {
            'nombre': 'Vestido Midi Lino',
            'marca': 'Aument Studio',
            'precio': 89,
            'precio_anterior': 119,
            'descripcion': 'Un vestido de lino natural de corte midi.',
            'emoji_preview': '👗',
            'categoria': ropa,
            'es_nuevo': True
        },
        {
            'nombre': 'Bolso Cuero Toscano',
            'marca': 'Artisana',
            'precio': 145,
            'descripcion': 'Elaborado a mano con cuero vacuno toscano.',
            'emoji_preview': '👜',
            'categoria': acc,
        },
        {
            'nombre': 'Sneakers Minimal',
            'marca': 'Step Studio',
            'precio': 112,
            'precio_anterior': 140,
            'descripcion': 'Diseño minimalista con suela de goma.',
            'emoji_preview': '👟',
            'categoria': cal,
            'en_oferta': True
        },
        {
            'nombre': 'Vela Aromática Premium',
            'marca': 'Maison',
            'precio': 38,
            'descripcion': 'Vela de soja natural con esencia de sándalo.',
            'emoji_preview': '🕯️',
            'categoria': hogar,
            'es_nuevo': True
        }
    ]

    for p_data in productos_data:
        Producto.objects.get_or_create(**p_data)

    print("Datos iniciales cargados con éxito.")

if __name__ == '__main__':
    populate()
