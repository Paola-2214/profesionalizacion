from django.contrib import admin
from .models import Cotizacion,Notificacion
@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display=('id','nombre','servicio','precio','decision','estado','fecha')
    list_filter=('estado','decision','servicio')
    search_fields=('nombre','correo')
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display=('id','usuario','titulo','leida','fecha')
