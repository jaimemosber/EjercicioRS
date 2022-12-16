#encoding:utf-8

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Artista(models.Model):
    IdArtista = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, verbose_name='Artista', unique=True)
    Url = models.URLField(verbose_name='URL')
    PictureUrl = models.URLField(verbose_name='URL de la foto')

    def __str__(self):
        return self.nombre

class Etiqueta(models.Model):
    IdTag = models.IntegerField(primary_key=True)
    TagValue = models.CharField(max_length=30, verbose_name='Valor de la etiqueta')

    def __str__(self):
        return str(self.TagValue)


class UsuarioArtista(models.Model):
    IdUsuario = models.IntegerField(verbose_name='Id del usuario')
    IdArtista = models.ForeignKey(Artista,on_delete=models.CASCADE)
    TiempoEscucha = models.IntegerField(verbose_name='Tiempo de escucha')
    
    def __str__(self):
        return str(self.TiempoEscucha)

class UsuarioEtiquetaArtista(models.Model):
    IdUsuario = models.IntegerField(verbose_name='Id del usuario')
    IdArtista = models.ForeignKey(Artista,on_delete=models.CASCADE)
    IdTag = models.ForeignKey(Etiqueta,on_delete=models.CASCADE)
    Dia = models.IntegerField(verbose_name='Día')
    Mes = models.IntegerField(verbose_name='Mes')
    Ano = models.IntegerField(verbose_name='Ano')

    def __str__(self):
        return str(self.IdUsuario) + ',' + str(self.IdArtista)
