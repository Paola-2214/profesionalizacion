from .models import Notificacion
def notifications(request):
    n=Notificacion.objects.filter(usuario=request.user,leida=False).count() if request.user.is_authenticated else 0
    return {'notificaciones_pendientes':n if request.user.is_authenticated and not request.user.is_staff else 0,'notificaciones_admin_pendientes':n if request.user.is_authenticated and request.user.is_staff else 0}
