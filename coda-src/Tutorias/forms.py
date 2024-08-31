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
