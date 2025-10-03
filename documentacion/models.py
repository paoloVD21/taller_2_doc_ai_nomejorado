from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from typing import Any, List, Tuple

class SecurityQuestions(models.Model):
    PREGUNTAS_CHOICES = [
        ('color', '¿Cuál es tu color favorito?'),
        ('comida', '¿Cuál es tu comida favorita?'),
        ('pelicula', '¿Cuál es tu película favorita?'),
        ('libro', '¿Cuál es tu libro favorito?'),
        ('deporte', '¿Cuál es tu deporte favorito?'),
        ('musica', '¿Cuál es tu género de música favorito?')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pregunta1 = models.CharField(max_length=50, choices=PREGUNTAS_CHOICES)
    respuesta1 = models.CharField(max_length=100)
    pregunta2 = models.CharField(max_length=50, choices=PREGUNTAS_CHOICES)
    respuesta2 = models.CharField(max_length=100)
    pregunta3 = models.CharField(max_length=50, choices=PREGUNTAS_CHOICES)
    respuesta3 = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Pregunta de Seguridad"
        verbose_name_plural = "Preguntas de Seguridad"

    def clean(self):
        # Verificar que no se repitan las preguntas
        preguntas = [self.pregunta1, self.pregunta2, self.pregunta3]
        if len(set(preguntas)) != 3:
            raise ValidationError('Las tres preguntas deben ser diferentes')

class Project(models.Model):
    nombre: models.CharField = models.CharField(max_length=100)
    descripcion: models.TextField = models.TextField(blank=True)
    propietario: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos')
    creado: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    actualizado: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self) -> str:
        return self.nombre

    @property
    def fases(self) -> models.QuerySet:
        return self.fase_set.all() # type: ignore


class Fase(models.Model):
    proyecto: models.ForeignKey = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='fases')
    nombre: models.CharField = models.CharField(max_length=100)

    class Meta:
        unique_together = ('proyecto', 'nombre')
        ordering = ['nombre']
        verbose_name = "Fase"
        verbose_name_plural = "Fases"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.proyecto.nombre})"


class SubArtefacto(models.Model):
    fase: models.ForeignKey = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='subartefactos')
    nombre: models.CharField = models.CharField(max_length=100)
    enlace: models.URLField = models.URLField(blank=True)

    class Meta:
        unique_together = ('fase', 'nombre')
        ordering = ['nombre']
        verbose_name = "Subartefacto"
        verbose_name_plural = "Subartefactos"

    def __str__(self) -> str:
        return f"{self.nombre} - {self.fase.nombre}"


class Artefacto(models.Model):
    TIPO_CHOICES: List[Tuple[str, str]] = [
        ('AREQ', 'Análisis de Requisitos'),
        ('DISE', 'Diseño'),
        ('DEVS', 'Desarrollo'),
        ('PRUE', 'Pruebas'),
        ('DESP', 'Despliegue'),
    ]

    proyecto: models.ForeignKey = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='artefactos')
    fase: models.ForeignKey = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='artefactos')
    subartefacto: models.ForeignKey = models.ForeignKey(SubArtefacto, on_delete=models.SET_NULL, null=True, blank=True, related_name='artefactos')

    tipo: models.CharField = models.CharField(max_length=4, choices=TIPO_CHOICES)
    titulo: models.CharField = models.CharField(max_length=100)
    contenido: models.TextField = models.TextField()
    contexto: models.TextField = models.TextField(blank=True, null=True)  # Nuevo campo para requisitos
    generado_por_ia: models.BooleanField = models.BooleanField(default=True)
    creado: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    actualizado: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = "Artefacto"
        verbose_name_plural = "Artefactos"

    def __str__(self) -> str:
        return f"{self.titulo} [{self.get_tipo_display()}]"
    
    def get_tipo_display(self) -> str:
        return dict(self.TIPO_CHOICES).get(self.tipo, "")
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.subartefacto and not self.fase:
            self.fase = self.subartefacto.fase
        super().save(*args, **kwargs)
        