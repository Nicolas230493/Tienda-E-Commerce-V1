from django.contrib import admin
from .models import Categoria, Producto, Newsletter, Pedido, ItemPedido, ImagenProducto, Perfil

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'emoji')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'precio', 'categoria', 'stock', 'es_nuevo', 'en_oferta')
    list_filter = ('categoria', 'es_nuevo', 'en_oferta')
    search_fields = ('nombre', 'marca')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenProductoInline]

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombre', 'fecha_registro')
    search_fields = ('email', 'nombre')

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'fecha', 'pagado')
    list_filter = ('pagado', 'fecha')
    inlines = [ItemPedidoInline]

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'ciudad')
