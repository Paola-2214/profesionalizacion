from django import template
from core.services import SERVICIOS
register=template.Library()
@register.filter
def imagen_servicio(nombre):
 return next((s['imagenes'][0] for s in SERVICIOS.values() if s['nombre']==nombre),'')
