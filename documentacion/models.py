from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.nombre


class Fase(models.Model):
    proyecto = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='fases')
    nombre = models.CharField(max_length=100)

    class Meta:
        unique_together = ('proyecto', 'nombre')
        ordering = ['nombre']
        verbose_name = "Fase"
        verbose_name_plural = "Fases"

    def __str__(self):
        return f"{self.nombre} ({self.proyecto.nombre})"


class SubArtefacto(models.Model):
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='subartefactos')
    nombre = models.CharField(max_length=100)
    enlace = models.URLField(blank=True)

    class Meta:
        unique_together = ('fase', 'nombre')
        ordering = ['nombre']
        verbose_name = "Subartefacto"
        verbose_name_plural = "Subartefactos"

    def __str__(self):
        return f"{self.nombre} - {self.fase.nombre}"


class Artefacto(models.Model):
    TIPO_CHOICES = [
        ('AREQ', 'Análisis de Requisitos'),
        ('DISE', 'Diseño'),
        ('DEVS', 'Desarrollo'),
        ('PRUE', 'Pruebas'),
        ('DESP', 'Despliegue'),
    ]

    proyecto = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='artefactos')
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='artefactos')
    subartefacto = models.ForeignKey(SubArtefacto, on_delete=models.SET_NULL, null=True, blank=True, related_name='artefactos')

    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    contexto = models.TextField(blank=True, null=True)  # Nuevo campo para requisitos
    generado_por_ia = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = "Artefacto"
        verbose_name_plural = "Artefactos"

    def __str__(self):
        return f"{self.titulo} [{self.get_tipo_display()}]"
    
    def save(self, *args, **kwargs):
        if self.subartefacto and not self.fase:
            self.fase = self.subartefacto.fase
        super().save(*args, **kwargs)
        