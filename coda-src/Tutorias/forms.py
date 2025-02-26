from django import forms
from .models import Tutoria, Plantilla
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

class FormReporte(forms.ModelForm):
    oficio = forms.CharField(required=False)
    tutor_firma = forms.MultipleChoiceField(choices=TEMAS)
    # tutor_firma = forms.CharField(widget=forms.Textarea, max_length=255, required=False)
    fecha = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    plantilla = forms.ModelChoiceField(queryset=Plantilla.objects.values_list('titulo',flat=True))
    tem = forms.CheckboxInput()

    class Meta:
        model = Plantilla
        fields = ['oficio', 'tutor_firma', 'fecha']

