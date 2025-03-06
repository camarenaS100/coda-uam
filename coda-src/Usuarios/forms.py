from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Tutor, Alumno, Cordinador, Usuario, Documento
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
    archivo = forms.FileField(
        label="Seleccionar archivo",
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": ".xls,.xlsx,.csv"}),
    )

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que el campo "nombre" no sea obligatorio si ya existe un archivo
        if self.instance and self.instance.archivo:
            self.fields['nombre'].required = False