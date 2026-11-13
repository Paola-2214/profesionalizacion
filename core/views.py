from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError,transaction
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Cotizacion,Notificacion
from .services import SERVICIOS

SERVICIOS_VALIDOS=[s['nombre'] for s in SERVICIOS.values()]
IMAGENES={s['nombre']:s['imagenes'][0] for s in SERVICIOS.values()}
def error(msg,status=400): return HttpResponse(msg,status=status)
def admin_only(request): return request.user.is_staff
def aviso(usuario,cotizacion,titulo,mensaje): Notificacion.objects.create(usuario=usuario,cotizacion=cotizacion,titulo=titulo,mensaje=mensaje)
def inicio(request): return render(request,'index.html')
def detalle_servicio(request,slug):
    servicio=SERVICIOS.get(slug)
    if not servicio: return error('Servicio no encontrado.',404)
    return render(request,'servicio.html',{'servicio':servicio})
@login_required
def cotizacion(request):
    if request.method=='POST':
        nombre=request.POST.get('nombre','').strip(); correo=request.POST.get('correo','').strip(); servicio=request.POST.get('servicio','').strip(); descripcion=request.POST.get('descripcion','').strip()
        if not all((nombre,correo,servicio,descripcion)): return error('Debes completar todos los campos.')
        try: validate_email(correo)
        except ValidationError: return error('Ingresa un correo electrónico válido.')
        if servicio not in SERVICIOS_VALIDOS: return error('Selecciona un servicio válido.')
        Cotizacion.objects.create(nombre=nombre,correo=correo,servicio=servicio,descripcion=descripcion,usuario=request.user)
        return render(request,'cotizacion.html',{'exito':True})
    seleccionado=request.GET.get('servicio','')
    return render(request,'cotizacion.html',{'exito':False,'servicio_seleccionado':seleccionado if seleccionado in SERVICIOS_VALIDOS else ''})
def registro(request):
    if request.method=='POST':
        nombre=request.POST.get('nombre','').strip(); correo=request.POST.get('correo','').strip().lower(); contrasena=request.POST.get('contrasena','')
        if not all((nombre,correo,contrasena)): msg='Completa todos los campos.'
        else:
            try: validate_email(correo); msg=''
            except ValidationError: msg='Ingresa un correo electrónico válido.'
        if not msg and len(contrasena)<8: msg='La contraseña debe tener al menos 8 caracteres.'
        if not msg:
            try:
                with transaction.atomic(): User.objects.create_user(username=correo,email=correo,password=contrasena,first_name=nombre)
            except IntegrityError: msg='Este correo ya está registrado.'
        if msg: return render(request,'registro.html',{'mensaje':msg,'error':msg,'exito':False})
        return redirect('login')
    return render(request,'registro.html')
def login_view(request):
    if request.method=='POST':
        correo=request.POST.get('correo','').strip().lower(); contrasena=request.POST.get('contrasena','')
        usuario=authenticate(request,username=correo,password=contrasena)
        if usuario is not None:
            login(request,usuario)
            return redirect('administrador' if usuario.is_staff else 'inicio')
        return render(request,'login.html',{'error':'Correo o contraseña incorrectos.'})
    return render(request,'login.html')
@require_POST
def logout_view(request): logout(request); return redirect('inicio')
@login_required
def administrador(request):
    if not admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    qs=Cotizacion.objects.all().order_by('-id')
    return render(request,'admin.html',{'cotizaciones':qs,'total_cotizaciones':qs.count(),'total_clientes':User.objects.filter(is_staff=False).count(),'total_mantenimiento':qs.filter(servicio=SERVICIOS_VALIDOS[0]).count(),'total_web':qs.filter(servicio=SERVICIOS_VALIDOS[1]).count(),'total_redes':qs.filter(servicio=SERVICIOS_VALIDOS[2]).count()})
@login_required
@require_POST
def asignar_precio(request,cotizacion_id):
    if not admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    try:
        precio=Decimal(request.POST.get('precio','').strip())
        if not precio.is_finite() or precio<=0 or precio>Decimal('99999999.99') or precio.as_tuple().exponent < -2: return error('Ingresa un precio positivo con máximo dos decimales.')
    except (InvalidOperation,ValueError): return error('Ingresa un precio válido.')
    with transaction.atomic():
        c=Cotizacion.objects.select_for_update().filter(pk=cotizacion_id,decision='Pendiente').first()
        if not c: return error('Cotización no encontrada o ya respondida.',404)
        c.precio=precio;c.save(update_fields=['precio'])
        aviso(c.usuario,c,'¡Ya tienes una propuesta de precio!',f'TechSolutions ha propuesto un precio de ${precio:,.2f} MXN para tu servicio de {c.servicio}. Entra a Mis cotizaciones para aceptarlo o rechazarlo.')
    return redirect('administrador')
@login_required
@require_POST
def decidir_cotizacion(request,cotizacion_id):
    if admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    decision=request.POST.get('decision','')
    if decision not in ('Aceptada','Rechazada'): return error('Decisión no válida.')
    with transaction.atomic():
        c=Cotizacion.objects.select_for_update().filter(pk=cotizacion_id,usuario=request.user).first()
        if not c: return error('Cotización no encontrada.',404)
        if c.precio is None or c.decision!='Pendiente': return error('Esta cotización no puede responderse.')
        c.decision=decision;c.fecha_aceptacion=timezone.now() if decision=='Aceptada' else None;c.save(update_fields=['decision','fecha_aceptacion'])
        for a in User.objects.filter(is_staff=True): aviso(a,c,f'Cotización {decision.lower()}',f'El cliente {request.user.first_name} {decision.lower()} la cotización #{c.pk} de {c.servicio}.')
    return redirect('panel_cliente')
@login_required
def panel_cliente(request):
    if admin_only(request): return redirect('administrador')
    qs=Cotizacion.objects.filter(usuario=request.user).order_by('-id')
    return render(request,'cliente.html',{'cotizaciones':qs,'total_cotizaciones':qs.count(),'pendientes':qs.filter(estado='Pendiente').count(),'en_proceso':qs.filter(estado='En proceso').count(),'finalizadas':qs.filter(estado='Finalizada').count()})
@login_required
@require_POST
def cambiar_estado(request,cotizacion_id):
    if not admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    with transaction.atomic():
        c=Cotizacion.objects.select_for_update().filter(pk=cotizacion_id).first()
        if not c: return error('Cotización no encontrada.',404)
        if c.decision!='Aceptada': return error('El cliente debe aceptar la cotización primero.')
        transiciones={'Pendiente':'En proceso','En proceso':'Finalizada'}
        nuevo=request.POST.get('estado','')
        if transiciones.get(c.estado)!=nuevo: return error('Debes seguir el orden de los estados.')
        c.estado=nuevo
        if nuevo=='En proceso':
            c.fecha_inicio=timezone.now();titulo='Tu servicio está en proceso';mensaje=f'Comenzamos a trabajar en tu servicio de {c.servicio}.'
        else:
            c.fecha_finalizacion=timezone.now();titulo='¡Tu servicio fue finalizado!';mensaje=f'El servicio de {c.servicio} ha sido completado.'
        c.save();aviso(c.usuario,c,titulo,mensaje)
    return redirect('administrador')
@login_required
def mis_contrataciones(request):
    if admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    return render(request,'contrataciones.html',{'contrataciones':Cotizacion.objects.filter(usuario=request.user,decision='Aceptada').order_by('-id'),'imagenes':IMAGENES})
@login_required
def detalle_contratacion(request,cotizacion_id):
    if admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    c=get_object_or_404(Cotizacion,pk=cotizacion_id,usuario=request.user,decision='Aceptada')
    servicio=next((s for s in SERVICIOS.values() if s['nombre']==c.servicio),None)
    if not servicio: return error('Información del servicio no disponible.',404)
    return render(request,'detalle_contratacion.html',{'contratacion':c,'servicio':servicio})
@login_required
def notificaciones(request):
    if admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    qs=Notificacion.objects.filter(usuario=request.user).order_by('-fecha','-id')
    return render(request,'notificaciones.html',{'avisos':qs,'no_leidas':qs.filter(leida=False).count()})
@login_required
@require_POST
def marcar_notificacion_leida(request,notificacion_id):
    if admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    Notificacion.objects.filter(pk=notificacion_id,usuario=request.user).update(leida=True)
    return redirect('notificaciones')
@login_required
def notificaciones_admin(request):
    if not admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    qs=Notificacion.objects.filter(usuario=request.user).order_by('-fecha','-id')
    return render(request,'notificaciones_admin.html',{'avisos':qs,'no_leidas':qs.filter(leida=False).count()})
@login_required
@require_POST
def marcar_notificacion_admin_leida(request,notificacion_id):
    if not admin_only(request): return HttpResponseForbidden('Acceso denegado.')
    Notificacion.objects.filter(pk=notificacion_id,usuario=request.user).update(leida=True)
    return redirect('notificaciones_admin')
