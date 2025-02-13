from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Tutor, Alumno, Cordinador, Usuario
from .constants import CARRERAS
from django.contrib.auth.forms import UserCreationForm

class FormUsuario(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['matricula', 'email', 'correo_personal']

class FormTutor(FormUsuario):
    
    class Meta:
        model = Tutor
        fields = ['first_name', 'last_name', 'matricula', 'email', 'correo_personal', 'cubiculo', 'coordinacion', 'password1', 'password2']
    pass

class FormCordinador(FormUsuario):
    class Meta:
        model = Cordinador
        fields = ['first_name', 'last_name', 'matricula', 'email', 'correo_personal', 'cubiculo', 'coordinacion', 'password1', 'password2']
    pass


class FormAlumno(FormUsuario):
    carrera = forms.ChoiceField(choices=CARRERAS)
    tutor_asignado = forms.ModelChoiceField(queryset=Tutor.objects.all(), empty_label="Seleccione tutor")

    class Meta:
        model = Alumno
        fields = ['first_name', 'last_name', 'matricula', 'email', 'correo_personal', 'carrera', 'tutor_asignado', 'password1', 'password2']
    pass

class ImportAlumnosForm(forms.Form):
    archivo = forms.FileField(label="Selecciona el archivo que deseas subir (XSLX, XSL o CSV)")
    pass