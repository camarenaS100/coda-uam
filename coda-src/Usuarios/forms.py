from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Tutor, Alumno, Cordinador, Usuario, Documento
from .constants import ALUMNO, TUTOR, COORDINADOR, CODA, CARRERAS, ESTADOS_ALUMNO, SEXOS
from django.contrib.auth.forms import UserCreationForm

class FormUsuario(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['matricula', 'email', 'correo_personal']

class FormTutor(FormUsuario):
    sexo = forms.ChoiceField(choices=SEXOS)

    class Meta:
        model = Tutor
        fields = ['first_name', 'second_last_name' ,'last_name', 'sexo','matricula', 'email', 'correo_personal', 'cubiculo', 'coordinacion', 'password1', 'password2', 'es_coordinador']
    pass

    def save(self, commit=True):
        user = super().save(commit=False)

        # Asegúrate de que es un tutor
        user.rol = [TUTOR]

        if commit:
            user.save()
        return user

class FormCordinador(FormUsuario):
    sexo = forms.ChoiceField(choices=SEXOS)
    
    class Meta:
        model = Cordinador
        fields = ['first_name', 'last_name' ,'second_last_name', 'sexo', 'matricula', 'email', 'correo_personal', 'cubiculo', 'coordinacion', 'password1', 'password2', 'es_tutor']
    pass

    def save(self, commit=True):
        user = super().save(commit=False)

        # Asegúrate de que es un coordinador
        user.rol = [COORDINADOR]
        user.sexo = self.cleaned_data['sexo']  # <- Aquí está el fix


        if commit:
            user.save()
        return user


class FormAlumno(FormUsuario):
    carrera = forms.ChoiceField(choices=CARRERAS)
    tutor_asignado = forms.ModelChoiceField(queryset=Tutor.objects.all(), empty_label="Seleccione tutor")
    estado = forms.ChoiceField(choices=ESTADOS_ALUMNO)
    trimestre_ingreso = forms.CharField(max_length=30)
    rfc = forms.CharField(max_length=30)
    sexo = forms.ChoiceField(choices=SEXOS)

    class Meta:
        model = Alumno
        fields = ['first_name', 'last_name', 'matricula', 'email', 'correo_personal', 'carrera', 'tutor_asignado', 'password1', 'password2',
                  'second_last_name', 'rfc', 'sexo', 'trimestre_ingreso', 'estado']
    pass

    def save(self, commit=True):
        user = super().save(commit=False)

        # Asegúrate de que es un alumno
        user.rol = [ALUMNO]

        if commit:
            user.save()
        return user

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