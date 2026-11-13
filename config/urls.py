from django.contrib import admin
from django.urls import path
from core import views
urlpatterns = [
 path('django-admin/',admin.site.urls),
 path('',views.inicio,name='inicio'),
 path('servicios/<slug:slug>',views.detalle_servicio,name='detalle_servicio'),
 path('cotizacion',views.cotizacion,name='cotizacion'),
 path('registro',views.registro,name='registro'),
 path('login',views.login_view,name='login'),
 path('logout',views.logout_view,name='logout'),
 path('admin',views.administrador,name='administrador'),
 path('admin/cotizacion/<int:cotizacion_id>/precio',views.asignar_precio,name='asignar_precio'),
 path('cliente/cotizacion/<int:cotizacion_id>/decision',views.decidir_cotizacion,name='decidir_cotizacion'),
 path('cliente',views.panel_cliente,name='panel_cliente'),
 path('admin/cotizacion/<int:cotizacion_id>/estado',views.cambiar_estado,name='cambiar_estado'),
 path('mis-contrataciones',views.mis_contrataciones,name='mis_contrataciones'),
 path('mis-contrataciones/<int:cotizacion_id>',views.detalle_contratacion,name='detalle_contratacion'),
 path('notificaciones',views.notificaciones,name='notificaciones'),
 path('notificaciones/<int:notificacion_id>/leer',views.marcar_notificacion_leida,name='marcar_notificacion_leida'),
 path('admin/notificaciones',views.notificaciones_admin,name='notificaciones_admin'),
 path('admin/notificaciones/<int:notificacion_id>/leer',views.marcar_notificacion_admin_leida,name='marcar_notificacion_admin_leida'),
]
