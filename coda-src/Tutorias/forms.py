from django import forms
from .models import Tutoria
from Usuarios.models import Documento
from .constants import TEMAS, ESTADO, ACEPTADO, PENDIENTE, DURACION_ASESORIA

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

class FormSeguimiento(forms.ModelForm):
    asistencia = forms.BooleanField(required=False)
    duracion = forms.ChoiceField(choices=DURACION_ASESORIA, required=False)
    firma_documentos_beca = forms.BooleanField(required=False)
    beca_otorgada = forms.CharField(max_length=255, required=False)
    asesoria_especializada = forms.BooleanField(required=False)
    observaciones = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)
    impacto_tutoria = forms.IntegerField(required=False)
    resultados_tutoria = forms.CharField(widget=forms.Textarea, max_length=1000, required=False)

    class Meta:
        model = Tutoria
        fields = ['asistencia', 'duracion', 'firma_documentos_beca', 'beca_otorgada', 'asesoria_especializada', 'observaciones', 'impacto_tutoria', 'resultados_tutoria']
        exclude = ['alumno', 'tutor', 'tema', 'fecha', 'descripcion', 'estado']


class FormReporte(forms.ModelForm):
    oficio = forms.CharField(required=False)
    fecha = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    plantilla = forms.ModelChoiceField(queryset=Documento.objects.all(), to_field_name='nombre', label="Selecciona una plantilla")
    tutor = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    carrera = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Documento
        fields = ['oficio', 'plantilla', 'fecha']

    def __init__(self, *args, tutor_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if tutor_instance:
            full_name = ""
            # Llenamos el nombre del tutor.
            if tutor_instance.sexo:
                if tutor_instance.sexo == "F":
                    full_name = "Dra."
                else:
                    full_name = "Dr."
                pass
            full_name += f" {tutor_instance.first_name} {tutor_instance.last_name}"
            if tutor_instance.second_last_name:
                full_name += f" {tutor_instance.second_last_name}"
            self.fields['tutor'].initial = full_name

        carreras_dict = dict([
            ("MAT", "Matemáticas Aplicadas"),
            ("COM", "Ingeniería en Computación"),
            ("IB", "Ingeniería Biológica"),
            ("BM", "Biología Molecular"),
        ])

        self.fields['carrera'].initial = carreras_dict.get(tutor_instance.coordinacion, "Carrera desconocida")

class FormCartasDeAsignacion(forms.ModelForm):
    no_inicio = forms.IntegerField(min_value=0)
    no_cartas = forms.IntegerField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    oficio = forms.CharField(required=False)
    fecha = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    plantilla = forms.ModelChoiceField(queryset=Documento.objects.all(), to_field_name='nombre', label="Selecciona una plantilla")
    tutor = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    carrera = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Documento
        fields = ['oficio', 'plantilla', 'fecha', 'no_inicio']

    def __init__(self, *args, tutor_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if tutor_instance:
            full_name = ""
            # Llenamos el nombre del tutor.
            if tutor_instance.sexo:
                if tutor_instance.sexo == "F":
                    full_name = "Dra."
                else:
                    full_name = "Dr."
                pass
            full_name += f" {tutor_instance.first_name} {tutor_instance.last_name}"
            if tutor_instance.second_last_name:
                full_name += f" {tutor_instance.second_last_name}"
            self.fields['tutor'].initial = full_name

        carreras_dict = dict([
            ("MAT", "Matemáticas Aplicadas"),
            ("COM", "Ingeniería en Computación"),
            ("IB", "Ingeniería Biológica"),
            ("BM", "Biología Molecular"),
        ])

        self.fields['carrera'].initial = carreras_dict.get(tutor_instance.coordinacion, "Carrera desconocida")

class FormReporteDeTutorias(forms.ModelForm):
    
    oficio = forms.CharField(required=True)
    fecha_inicio = forms.DateField(required=True)
    fecha_fin = forms.DateField(required=True)
    fecha = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=True)
    plantilla = forms.ModelChoiceField(queryset=Documento.objects.all(), to_field_name='nombre', label="Selecciona una plantilla", required=True)
    tutor = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Documento
        fields = ['oficio', 'plantilla', 'fecha', 'fecha_inicio', 'fecha_fin']

    def __init__(self, *args, tutor_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tutor_instance:
                full_name = ""
                # Llenamos el nombre del tutor.
                if tutor_instance.sexo:
                    if tutor_instance.sexo == "F":
                        full_name = "Dra."
                    else:
                        full_name = "Dr."
                    pass
                full_name += f" {tutor_instance.first_name} {tutor_instance.last_name}"
                if tutor_instance.second_last_name:
                    full_name += f" {tutor_instance.second_last_name}"
                self.fields['tutor'].initial = full_name