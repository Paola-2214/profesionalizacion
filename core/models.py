from django.db import models
from django.contrib.auth.models import User

class Cotizacion(models.Model):
    nombre=models.CharField(max_length=200)
    correo=models.EmailField()
    servicio=models.CharField(max_length=150)
    descripcion=models.TextField()
    fecha=models.DateTimeField(auto_now_add=True)
    estado=models.CharField(max_length=30,default='Pendiente')
    usuario=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cotizaciones')
    precio=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    decision=models.CharField(max_length=30,default='Pendiente')
    fecha_aceptacion=models.DateTimeField(null=True,blank=True)
    fecha_inicio=models.DateTimeField(null=True,blank=True)
    fecha_finalizacion=models.DateTimeField(null=True,blank=True)
    def __str__(self): return f'#{self.pk} {self.servicio}'

class Notificacion(models.Model):
    usuario=models.ForeignKey(User,on_delete=models.CASCADE,related_name='avisos')
    cotizacion=models.ForeignKey(Cotizacion,on_delete=models.CASCADE,null=True,blank=True)
    titulo=models.CharField(max_length=200)
    mensaje=models.TextField()
    leida=models.BooleanField(default=False)
    fecha=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.titulo
