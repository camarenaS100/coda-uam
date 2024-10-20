from django import forms
from .models import Tutoria
from .constants import TEMAS, ESTADO, ACEPTADO, PENDIENTE

class FormTutorias(forms.ModelForm):

    alumno = forms.CharField(disabled=True, required=False)
    tutor = forms.CharField(disabled=True, required=False)
    # tema = forms.ChoiceField(choices=TEMAS)
    #Despliega campo para multiples opciones
    tema = forms.MultipleChoiceField(choices=TEMAS)
    fecha = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    descripcion = forms.CharField(widget=forms.Textarea, max_length=255, required=False)
    estado = forms.ChoiceField(choices=ESTADO, required=False)


    class Meta:
        model = Tutoria
        fields = ['tema', 'fecha', 'descripcion']

# class FormSeguimiento(forms.ModelForm):    #esto se debería de usar?
#     asistencia = forms.BooleanField(required=False)
#     duracion = forms.ChoiceField(choices=DURACION_ASESORIA, required=False)
#     firma_documentos_beca = forms.BooleanField(required=False)
#     beca_otorgada = forms.CharField(max_length=255, required=False)
#     asesoria_especializada = forms.BooleanField(required=False)
#     observaciones = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)
#     impacto_tutoria = forms.IntegerField(required=False)
#     resultados_tutoria = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)

#     class Meta:
#         model = Tutoria
#         fields = ['asistencia', 'duracion', 'firma_documentos_beca', 'beca_otorgada', 'asesoria_especializada', 'observaciones', 'impacto_tutoria', 'resultados_tutoria']
#         exclude = ['alumno', 'tutor', 'tema', 'fecha', 'descripcion', 'estado']

