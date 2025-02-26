from django.db import models
from django.contrib.postgres.fields import ArrayField
from Usuarios.models import Alumno, Tutor
from .constants import TEMAS, SERVICIO, PENDIENTE, ESTADO

# Create your models here.
class Tutoria(models.Model):


    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    # tema = models.CharField(SERVICIO, max_length=4, choices=TEMAS, default=SERVICIO)
    # Se cambia el campo para que sea una lista
    tema = ArrayField(models.CharField(SERVICIO, max_length=4, choices=TEMAS, default=SERVICIO))
    fecha = models.DateTimeField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(PENDIENTE, max_length=4, choices=ESTADO, default=PENDIENTE)

    def __str__(self) -> str:
        string_tutoria = f'{self.alumno.first_name} {self.alumno.last_name}: tutoria {self.pk}'
        return  string_tutoria
    
    class Meta:
        ordering = ["-fecha"]

    #Sobreescribir método get_foo_display de django
    def get_tema_display(self):
        # values = self.tema
        choices = dict(TEMAS)
        # return choices
        return [choices.get(t, "Unknown") for t in self.tema]
  
class Asesoria(models.Model):

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    tema = models.CharField(max_length=120)
    fecha = models.DateTimeField()
    descripcion = models.CharField(max_length=255)

class Plantilla(models.Model):
    titulo = models.CharField(max_length=120)
    archivo = models.FileField(null=True)
    