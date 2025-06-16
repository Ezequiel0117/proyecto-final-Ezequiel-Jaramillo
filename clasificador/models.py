from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from storages.backends.s3boto3 import S3Boto3Storage

class ProfilePictureStorage(S3Boto3Storage):
    location = 'profile_pics'
    default_acl = 'public-read'
    file_overwrite = False

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='', storage=ProfilePictureStorage(), blank=True, null=True)

    def __str__(self):
        return str(self.username)

    @property
    def total_residuos_reciclados(self):
        return self.imagen_residuo_set.aggregate(total=models.Sum('cantidad_residuos'))['total'] or 0

class ImagenResiduo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='imagen_residuo_set')
    imagen = models.ImageField(upload_to='residuos/')
    resultado = models.TextField(blank=True, null=True)
    cantidad_residuos = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username if self.user else 'No user'} - {self.imagen.name} ({self.cantidad_residuos} residuos)"
    

class PuntoReciclaje(models.Model):
    provincia = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()
    materiales = models.CharField(max_length=200)
    capacidad_kg = models.CharField(max_length=50)

    def str(self):
        return self.nombre
    
    
