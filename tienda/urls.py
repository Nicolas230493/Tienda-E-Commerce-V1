from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path('carrito/obtener/', views.obtener_carrito, name='obtener_carrito'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/procesar/', views.procesar_pedido, name='procesar_pedido'),
    path('newsletter/suscribir/', views.suscribir_newsletter, name='suscribir_newsletter'),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
]
