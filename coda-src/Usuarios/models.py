from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .constants import ROLES, CARRERAS
from Tutorias.constants import TEMAS, OTRO
from .constants import CODA, TUTOR, COORDINADOR, ALUMNO, SEXOS, ESTADOS_ALUMNO

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

def usr_pfp_path(instance, filename):
    return f'Usuarios/fotos/usuario_{instance.user.matricula}/{filename}'

class Usuario(AbstractUser):
    

    username = None
    matricula = models.CharField(max_length=11,unique=True)
    foto = models.ImageField(null=True, blank=True, upload_to=usr_pfp_path)
    email = models.EmailField(unique=True)
    correo_personal = models.EmailField(max_length=50, blank=True, null=True)
    rol = models.CharField(max_length=8, choices=ROLES, default="USR")
    sexo = models.CharField(max_length=30, choices=SEXOS, null=True)
    #nombre = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['matricula']

    def __str__(self) -> str:
        return str(self.matricula)
    
    def get_rol(self) -> str:
        return str(self.rol)
    
    


    objects = UserManager()

class Tutor(Usuario):
    cubiculo = models.IntegerField()
    horario  = models.FileField(null=True, blank=True)
    coordinacion = models.CharField(max_length=30, choices=CARRERAS)
    es_coordinador = models.BooleanField(default=False)
    es_tutor = models.BooleanField(default=True)
    tema_tutorias = models.CharField(max_length=4,choices=TEMAS, default=OTRO) # Tema por defecto para las tutorias

    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'

    def save(self, commit=True) -> None:
        self.rol = TUTOR

        # Deprecated
        # if self.es_coordinador :
        #     self.rol = "COR"
            
        return super(Tutor, self).save()


class Coda(Usuario):
    cubiculo = models.IntegerField()
    horario  = models.FileField(null=True, blank=True)
    coordinacion = models.CharField(max_length=30, choices=CARRERAS)
    es_coordinador = models.BooleanField(default=False)
    tema_tutorias = models.CharField(max_length=4,choices=TEMAS, default=OTRO) # Tema por defecto para las tutorias

    class Meta:
        verbose_name = 'CODA'
        verbose_name_plural = 'CODAA'

    def save(self, commit=True) -> None:
        self.rol = CODA
        return super(Coda, self).save()
    


class Cordinador(Usuario):
    cubiculo = models.IntegerField()
    horario = models.FileField(null=True, blank=True)
    coordinacion = models.CharField(max_length=30, choices=CARRERAS)
    es_coordinador = models.BooleanField(default=True)
    es_tutor = models.BooleanField(default=False)
    tutor_tutorias = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cordinador'
        verbose_name_plural = 'Cordinadores'

    def save(self, *args, **kwargs):
        self.rol = COORDINADOR
        super().save(*args, **kwargs)  # Guarda el Cordinador primero

        if self.es_tutor:
            # Si es tutor, asegurarse de que también está en la tabla Tutor
            tutor, created = Tutor.objects.update_or_create(
                email=self.email,
                defaults={
                    "matricula": self.matricula,
                    "first_name": self.first_name,
                    "last_name": self.last_name,
                    "cubiculo": self.cubiculo,
                    "horario": self.horario,
                    "coordinacion": self.coordinacion,
                    "es_coordinador": True,  # Para reflejar su rol como coordinador también
                    "es_tutor": True,
                    "tema_tutorias": OTRO,  # Valor por defecto
                }
            )

    def delete(self, *args, **kwargs):
        # Si el Coordinador es eliminado, también eliminar su entrada como Tutor si existe
        Tutor.objects.filter(email=self.email).delete()
        super().delete(*args, **kwargs)


def alumno_trayectoria_path(instance, filename):
    return f'Usuarios/trayectorias/alumno_{instance.user.matricula}/{filename}'

class Alumno(Usuario):
    
    carrera = models.CharField(max_length=30, choices=CARRERAS)
    trayectoria = models.FileField(null=True, blank=True, upload_to=alumno_trayectoria_path)
    tutor_asignado = models.ForeignKey(Tutor, on_delete=models.PROTECT)
    estado = models.IntegerField( choices=ESTADOS_ALUMNO, null=True)

    def save(self, commit=True) -> None:
        self.rol = ALUMNO
        return super(Alumno, self).save()
    
    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    #@property
    #def get_tutor_fullname(self) -> str:
    #    return f'{self.tutor_asignado.first_name} {self.tutor_asignado.last_name}'




# class Coordinador(Usuario):
#     coordinacion = models.CharField(max_length=30, choices=CARRERAS)
#     class Meta:
#         verbose_name = 'Coordinador'
#         verbose_name_plural = 'Coordinadores'
