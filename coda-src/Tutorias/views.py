import qrcode
from typing import Any, Dict
from django.shortcuts import get_object_or_404, redirect
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import View
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail

from datetime import datetime, timedelta

from .models import Tutoria
from .forms import FormTutorias
from .constants import PENDIENTE, ACEPTADO, RECHAZADO
from Usuarios.constants import TUTOR, ALUMNO, COORDINADOR, TEMPLATES, CORREO
from Usuarios.views import BaseAccessMixin, CodaViewMixin, TutorViewMixin, AlumnoViewMixin, CordinadorViewMixin
from Usuarios.models import Tutor, Alumno, Cordinador
from notifications.signals import notify
from smtplib import SMTPException

from django.http import FileResponse
from django.utils import timezone
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.shortcuts import get_object_or_404

#Funcion para descargar pdf
def generar_pdf(request):
    tutor_loggeado = get_object_or_404(Tutor, pk=request.user)

    # Obtener las fechas seleccionadas del formulario HTML
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin') 

    # Convertir las fechas de cadena a objetos de fecha si se han proporcionado
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = timezone.datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        fecha_fin = timezone.datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)

        # Filtrar las tutorías por las fechas seleccionadas
        tutorias_tutor = Tutoria.objects.filter(tutor=tutor_loggeado, fecha__range=(fecha_inicio, fecha_fin))
    else:
        # Si no se han proporcionado fechas, obtener todas las tutorías del tutor
        tutorias_tutor = Tutoria.objects.filter(tutor=tutor_loggeado)

    # Crear un buffer de bytes para almacenar el PDF
    buffer = BytesIO()

    # Crear el objeto PDF usando el buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Encabezado del PDF
    header_style = ParagraphStyle(name='HeaderStyle', fontSize=12)
    header_text = 'Historial tutorias'
    header_paragraph = Paragraph(header_text, header_style)
    elements.append(header_paragraph)

    # Agregar nombre del tutor
    tutor_name = f'Nombre Tutor: {tutor_loggeado.first_name} {tutor_loggeado.last_name}'
    tutor_name_paragraph = Paragraph(tutor_name, header_style)
    elements.append(tutor_name_paragraph)

    # Agregar un espacio en blanco para separar el nombre del tutor de la tabla
    elements.append(Spacer(1, 12))  # Ajusta el segundo valor para controlar la altura de la separación

    # Agregar datos como una tabla
    data = [["Alumno", 'Fecha', 'Hora', 'Tema', 'Notas']]

    for tutoria in tutorias_tutor:
        data.append([
            f"{tutoria.alumno.first_name} {tutoria.alumno.last_name}",
            tutoria.fecha.strftime('%Y-%m-%d'),
            tutoria.fecha.strftime('%I:%M %p'),
            tutoria.get_tema_display(),
            tutoria.descripcion,
        ])

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white), 
        ('GRID', (0, 0), (-1, -1), 1, colors.orange), 
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), 
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12), 
    ])

    # Crear la tabla
    tabla = Table(data)
    tabla.setStyle(style)
    elements.append(tabla)

    # Construir el PDF
    doc.build(elements)

    # Resetear el buffer de bytes al inicio
    buffer.seek(0)

    # Devolver el PDF como una respuesta de archivo
    return FileResponse(buffer, as_attachment=True, filename='tabla.pdf')

#Generar archivo txt de tutorias
def generar_archivo_txt(request,pk):

    # Genera el contenido del archivo de texto (aquí es solo un ejemplo)
    tutor = Tutor.objects.get(pk=pk)
    tutorias = Tutoria.objects.filter(tutor=tutor)

    # Obtener las fechas seleccionadas del formulario HTML
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin') 

    # Convertir las fechas de cadena a objetos de fecha si se han proporcionado
    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = timezone.datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        fecha_fin = timezone.datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1)

        # Filtrar las tutorías por las fechas seleccionadas
        tutorias = Tutoria.objects.filter(tutor=tutor, fecha__range=(fecha_inicio, fecha_fin))
    else:
        # Si no se han proporcionado fechas, obtener todas las tutorías del tutor
        tutorias = Tutoria.objects.filter(tutor=tutor)
    
    contenido = "Tutorias \n"
    for tutoria in tutorias:
        contenido += f"Alumno: {tutoria.alumno.first_name} {tutoria.alumno.last_name}\n"
        contenido += f"Tutor: {tutoria.tutor.first_name} {tutoria.tutor.last_name}\n"
        contenido += f"Fecha: {tutoria.fecha}\n"
        contenido += f"Tema: {tutoria.get_tema_display()}\n"
        contenido += f"Notas: {tutoria.descripcion}\n\n"

    # Escribe el contenido en un archivo de texto
    with open("tutoria.txt", "w") as archivo:
        archivo.write(contenido)

    # Abre el archivo de texto y lo sirve como una respuesta HTTP para descargarlo
    with open("tutoria.txt", "rb") as archivo:
        response = HttpResponse(archivo.read(), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=archivo.txt'
        return response


# Create your views here.
def index(request):
    return HttpResponse("Tutorias app index placeholder")

class AceptarTutoriaView(View):
    def post(self, request, pk):
        tutoria = get_object_or_404(Tutoria, pk=pk)
        tutoria.estado = ACEPTADO
        tutoria.save()
        return redirect('Tutorias-tutor')  

class RechazarTutoriaView(View):
    def post(self, request, pk):
        tutoria = get_object_or_404(Tutoria, pk=pk)
        tutoria.estado = RECHAZADO
        tutoria.save()
        return redirect('Tutorias-tutor')    
    
class TutoriaUpdateView(BaseAccessMixin, UpdateView):
    model = Tutoria
    fields = ['tema', 'fecha', 'descripcion']

    success_url  = reverse_lazy('Tutorias-historial')

    template_name = 'Tutorias/editarTutoria.html'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        rol = self.request.user.get_rol()
        if rol == TUTOR:
            tutor = Tutor.objects.get(pk=self.request.user)
        recipient = Alumno.objects.filter(pk=self.get_object().alumno)

        notify.send(tutor, recipient=recipient, verb='Tutoria Modificada')
        return super().form_valid(form)
    
    
# Solicitud Tutorias
class TutoriaCreateView(AlumnoViewMixin, CreateView):
    #model = Tutoria
    #fields = ['tema', 'fecha', 'descripcion']

    form_class = FormTutorias

    template_name = 'Tutorias/solicitudTutoria.html'

    success_url = reverse_lazy('Tutorias-alumno')

    def form_valid(self, form: FormTutorias) -> HttpResponse:
        alumno = get_object_or_404(Alumno, pk=self.request.user)
        form.instance.alumno = alumno
        form.instance.tutor = alumno.tutor_asignado

        rol = self.request.user.get_rol()
        if rol == ALUMNO:
            recipient = Tutor.objects.get(pk=alumno.tutor_asignado)

        notify.send(alumno, recipient=recipient, verb='Nueva solicitud de tutoria', description=f'{form.instance.get_tema_display()}')
        
        # TODO utilizar una rutina para mandar los correos
        #send_mail(
         #   subject='Nueva solicitud de tutoria',
          #  message=f'Solicitud de tutoria creada por {alumno.get_full_name()} con tema: {form.instance.get_tema_display()}',
           # from_email=CORREO,
            #recipient_list=[recipient.email],
            #fail_silently=False
    
        

        return super().form_valid(form)

    def get_initial(self) -> dict[str, Any]:
        return super().get_initial()
    


# Ver Tutorias
# TODO Añadir verificación de permisos de acceso a la tutoria
class TutoriasDetailView(BaseAccessMixin, DetailView):
     
    model = Tutoria

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)

    template_name='Tutorias/verTutorias_tutor.html'

    def get_queryset(self) -> QuerySet[Any]:
        
        if Tutor.objects.filter(pk=self.request.user.pk).exists():
            # Tutorias correspondientes al tutor
            queryset = super().get_queryset().filter(tutor=self.request.user)
        else: 
            # Tutorias correspondientes al alumno
            queryset = super().get_queryset().filter(alumno=self.request.user)
        
        if self.request.user.is_superuser == 1: 
            # Muestra todas las tutorias para el primer usuario creado (generalmente el primer superuser)
            queryset = super().get_queryset().all()
        
        return queryset
    
class HistorialTutoriasListView(BaseAccessMixin, ListView):
     
    model = Tutoria
    template_name='Tutorias/historialtutoria.html'

    def get_queryset(self) -> QuerySet[Any]:
        
        if Tutor.objects.filter(pk=self.request.user.pk).exists():
            # Tutorias correspondientes al tutor
            queryset = super().get_queryset().filter(tutor=self.request.user.pk)
        else: 
            # Tutorias correspondientes al alumno
            queryset = super().get_queryset().filter(alumno=self.request.user)
        
        if self.request.user.is_superuser == 1: 
            # Muestra todas las tutorias para el primer usuario creado (generalmente el primer superuser)
            queryset = super().get_queryset().all()
        
        return queryset

class HistorialTutoriasGenerateView(BaseAccessMixin, ListView):
    model = Tutoria
    template_name = 'Tutorias/generarhistorialtutoria.html'

class VerTutoriasCoordinadorListView(CordinadorViewMixin, ListView):
    model = Tutoria
    template_name='Tutorias/verTutorias_cordinador.html'

    def get_queryset(self) -> QuerySet[Any]:
        
        coord = get_object_or_404(Cordinador, pk=self.request.user.pk)
        tutores = Tutor.objects.all().filter(coordinacion=coord.coordinacion)
        queryset = super().get_queryset().filter(tutor__in=tutores)   
        
        return queryset 
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        #tutor = Tutor.objects.get(pk=self.kwargs.get('pk'))
        coord = get_object_or_404(Cordinador, pk=self.request.user.pk)
        tutores = Tutor.objects.all().filter(coordinacion=coord.coordinacion)
        context["tutores"] = tutores

        return context
    
class VerTutoriasCoordinadorPorTutorListView(CordinadorViewMixin, ListView):
     
    model = Tutoria
    template_name='Tutorias/verTutorias_cordinador_portutor.html'

    def get_queryset(self) -> QuerySet[Any]:
        
        queryset = super().get_queryset().filter(tutor=self.kwargs.get('pk'))   
        
        return queryset 
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tutor = Tutor.objects.get(pk=self.kwargs.get('pk'))
        context["tutor"] = tutor
        return context


class VerTutoriasCodaListView(CodaViewMixin, ListView):    
    model = Tutoria
    template_name='Tutorias/verTutorias_cooda.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        
        queryset = super().get_queryset().filter(tutor=self.kwargs.get('pk'))   
        
        return queryset 
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tutor = Tutor.objects.get(pk=self.kwargs.get('pk'))
        context["tutor"] = tutor
        return context

class VerTutoresListView(CodaViewMixin, ListView):
    model = Tutor
    template_name = 'Tutorias/verTutores_coda.html'

class VerTutoresCoordListView(CordinadorViewMixin, ListView):
    model = Tutor
    template_name = 'Tutorias/verTutores_cordinador.html'

    def get_queryset(self) -> QuerySet[Any]:
        coord = get_object_or_404(Cordinador, pk=self.request.user.pk)

        queryset = super().get_queryset().filter(coordinacion=coord.coordinacion)
        return queryset
    
class VerTutoradosCodaListView(CodaViewMixin, ListView):
    model = Alumno
    template_name = 'Tutorias/verTutorados_coda.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        
        queryset = super().get_queryset().filter(tutor_asignado=self.kwargs.get('pk'))   
        
        return queryset 

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tutor = Tutor.objects.get(pk=self.kwargs.get('pk'))
        context["tutor"] = tutor
        return context
    
class VerTutoradosCoordinadorListView(CordinadorViewMixin, ListView):
    model = Alumno
    template_name = 'Tutorias/verTutorados_cordinador.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        
        queryset = super().get_queryset().filter(tutor_asignado=self.kwargs.get('pk'))   
        
        return queryset 

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tutor = Tutor.objects.get(pk=self.kwargs.get('pk'))
        context["tutor"] = tutor
        return context

class VerTutoriasTutorListView(TutorViewMixin, ListView):
     
    model = Tutoria
    template_name='Tutorias/verTutorias_tutor.html'

    def get_queryset(self) -> QuerySet[Any]:
        
        # Tutorias correspondientes al tutor
        queryset = super().get_queryset().filter(tutor=self.request.user)
    
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tutorados = Alumno.objects.filter(tutor_asignado=self.request.user)
        context["tutorados"] = [alumno for alumno in tutorados]
        return context


class VerTutoriasAlumnoListView(AlumnoViewMixin, ListView):
     
    model = Tutoria
    template_name='Tutorias/verTutorias_alumno.html'

    def get_queryset(self) -> QuerySet[Any]:
        
        # Tutorias correspondientes al alumno
        
        queryset = super().get_queryset().filter(alumno=self.request.user)
        #if self.request.user.is_superuser == 1: 
            # Muestra todas las tutorias para el primer usuario creado (generalmente el primer superuser)
            #queryset = super().get_queryset().all()
        
        return queryset
    

# TODO Eliminar para prod
# class DebugTutoriasView(LoginRequiredMixin, ListView):

#     model = Tutoria
#     template_name='Tutorias/verTutorias_coordinador.html'

#     def get_queryset(self) -> QuerySet[Any]:
#         return super().get_queryset()
    
    
class QuickCreateTutoriaView(AlumnoViewMixin, CreateView):
    model = Tutoria
    template_name = 'Tutorias/registrar-tutoria.html'
    success_url = reverse_lazy('login_success')

    form_class = FormTutorias

    def form_valid(self, form: FormTutorias) -> HttpResponse:
        alumno = get_object_or_404(Alumno, pk=self.request.user)
        form.instance.alumno = alumno
        form.instance.tutor = alumno.tutor_asignado
        form.instance.estado = ACEPTADO
        
        
        rol = self.request.user.get_rol()
        if rol == ALUMNO:
            recipient = alumno.tutor_asignado   # No sé que hace este bloque, pero no lo voy a quitar para que no se rompa. -Alfredo
        else:
            recipient = Alumno.objects.filter(pk=self.get_object().alumno)
        
        notify.send(alumno, recipient=recipient, verb='Tutoria registrada con QR')

        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        print("Tutoria invalida")
        print(f'Form: {form.instance}')
        return super().form_invalid(form)

    def get_initial(self) -> dict[str, Any]:
        super().get_initial()
        try:
            alumno = Alumno.objects.get(pk=self.request.user.pk)
        except Alumno.DoesNotExist:
            raise PermissionDenied("Sólo los alumnos pueden registrar tutorias con QR")
        self.initial["alumno"] = alumno
        self.initial["tutor"] = alumno.tutor_asignado
        self.initial["tema"] = alumno.tutor_asignado.tema_tutorias
        print(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        self.initial["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.initial["descripcion"] = "Tutoria registrada con QR"
        return self.initial 
      
    
class VerTutoradosTutorListView(TutorViewMixin, ListView):
     
    model = Alumno
    template_name='Tutorias/list_tutorados.html'

    def get_queryset(self) -> QuerySet[Any]:
        
        # Tutorias correspondientes al tutor
        queryset = super().get_queryset().filter(tutor_asignado=self.request.user)
    
        return queryset

# Este es para asesorias, aun no se va a usar
class QRCodeView(View):
    def get(self, request):
        # Obtengo el usuario
        user_id = request.user.id

        # Creo qr
        qr_content = f"User ID: {user_id}"

        # Crea el qr
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)


        img = qr.make_image(fill_color="black", back_color="white")

        # Mando htttppp
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")

        return response


class CrearTutoriaPorAlumnoView(TutorViewMixin, CreateView):
    model = Tutoria
    form_class = FormTutorias
    template_name = 'Tutorias/solicitudTutoria.html'
    success_url = reverse_lazy('login_success')  # Cambia esto a la URL adecuada

    def form_valid(self, form):
        # Obtén el nombre del alumno desde la URL
        alumno_pk = self.kwargs.get('pk_alumno')

        # Busca el alumno por nombre
        alumno = get_object_or_404(Alumno, pk=alumno_pk)

        # Completa el formulario con los datos del alumno
        form.instance.alumno = alumno
        form.instance.tutor = alumno.tutor_asignado

        # Genera un slug único para la tutoría (puedes ajustar esto según tus necesidades)
        slug = slugify(form.instance.tema)
        form.instance.slug = slug

        return super().form_valid(form)
