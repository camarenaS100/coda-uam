import qrcode
from typing import Any, Dict
from django.shortcuts import get_object_or_404, redirect
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import View
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.contrib import messages
from datetime import datetime, timedelta

from .models import Tutoria
from .forms import FormTutorias, FormSeguimiento, FormReporte
# from .forms import FormSeguimiento # de nuevo, no estoy seguro, FormReporte
from .constants import PENDIENTE, ACEPTADO, RECHAZADO, DURACION_ASESORIA # de nuevo, no estoy seguro
from Usuarios.constants import TUTOR, ALUMNO, COORDINADOR, TEMPLATES, CORREO
from Usuarios.views import BaseAccessMixin, CodaViewMixin, TutorViewMixin, AlumnoViewMixin, CordinadorViewMixin
from Usuarios.models import Tutor, Alumno, Cordinador, Coda
from Usuarios.models import Documento
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
from django.shortcuts import get_object_or_404, get_list_or_404

import re, docx, os
from zipfile import ZipFile
from io import BytesIO

#Funcion para descargar pdf
def carta_tutorados_pdf(request):
    print(request)
    print(request.user)
    tutor_id = int(request.GET.get('tutor-id'))
    print(type(tutor_id))
    print(tutor_id)
    tutor = get_object_or_404(Tutor, matricula=tutor_id)
    print(tutor.coordinacion)
    tutorados = Alumno.objects.filter(tutor_asignado=tutor.pk)
    print(tutorados)
    print(type(tutorados))

    # Crear un buffer de bytes para almacenar el PDF
    buffer = BytesIO()

    # Crear el objeto PDF usando el buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Encabezado del PDF
    header_style = ParagraphStyle(name='HeaderStyle', fontSize=12)
    header_text = 'Asignación de tutorados'
    header_paragraph = Paragraph(header_text, header_style)
    elements.append(header_paragraph)

    # Agregar nombre del tutor
    tutor_name = f'Nombre Tutor: {tutor.first_name} {tutor.last_name}'
    tutor_name_paragraph = Paragraph(tutor_name, header_style)
    elements.append(tutor_name_paragraph)

    # Agregar un espacio en blanco para separar el nombre del tutor de la tabla
    elements.append(Spacer(1, 12))  # Ajusta el segundo valor para controlar la altura de la separación

    # Agregar párrafo
    parrafo = f"""Estimado doctor {tutor.last_name}, como parte del Sistema de Acompañamiento al 
    Alumnado que desarrolla la Universidad Autónoma Metropolitana Unidad Cuajimalpa y con la finalidad de
    propiciar el buen desempeño académico de nuestros alumnos y alumnas desde su ingreso a la Universidad y 
    hasta la conclusión de sus estudios, le comunico que tiene asignados los siguientes miembros del alumnado de 
    la licenciatura en Ingeniería en Computación para su Tutoría y Asesoría."""
    parr_paragraph = Paragraph(parrafo, header_style)
    elements.append(parr_paragraph)

    # Agregar un espacio en blanco para separar el nombre del tutor de la tabla
    elements.append(Spacer(1, 12))  # Ajusta el segundo valor para controlar la altura de la separación

    # Agregar datos como una tabla
    data = [["Trimestre de inicio","Matrícula", 'Apellido 1', 'Apellido 2', 'Nombre(s)']]

    for alumno in tutorados:
        data.append([
            None,
            alumno.matricula,
            alumno.last_name,
            None,
            alumno.first_name,
        ])
        print(f"Alumno completo: {alumno.matricula} {alumno.first_name} {alumno.last_name}")

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white), 
        ('GRID', (0, 0), (-1, -1), 1, colors.black), 
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
    return FileResponse(buffer, as_attachment=True, filename=f'{tutor.last_name.upper()}_TUTORES_ATENDIDOS_21-24.pdf')

#Funcion para descargar pdf
def generar_pdf(request):
    tutor_loggeado = get_object_or_404(Tutor, pk=request.user)

    # Obtener las fechas seleccionadas del formulario HTML
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin') 
    # Obtención de los checkbox
    alumno = request.GET.get('alumno') 
    fecha = request.GET.get('fecha') 
    hora = request.GET.get('hora') 
    tema = request.GET.get('tema') 
    notas = request.GET.get('notas') 
    todo = request.GET.get('todo')

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
    tutor_name = f'Nombre Tutor: {tutor_loggeado.first_name} {tutor_loggeado.last_name} {tutor_loggeado.second_last_name}'
    tutor_name_paragraph = Paragraph(tutor_name, header_style)
    elements.append(tutor_name_paragraph)

    # Agregar un espacio en blanco para separar el nombre del tutor de la tabla
    elements.append(Spacer(1, 12))  # Ajusta el segundo valor para controlar la altura de la separación

    # Agregar datos como una tabla
    data = [["Alumno", 'Fecha', 'Hora', 'Tema', 'Notas']]

    for tutoria in tutorias_tutor:
        data.append([
            f"{tutoria.alumno.first_name} {tutoria.alumno.last_name} {tutoria.alumno.second_last_name}",
            tutoria.fecha.strftime('%Y-%m-%d'),
            tutoria.fecha.strftime('%I:%M %p'),
            # tutoria.get_tema_display(),
            # Agregar lista de temas al pdf
            Paragraph(', '.join(tutoria.get_tema_display())),
            tutoria.descripcion,
        ])

    # Eliminación de columnas
    if todo == None:
        if alumno == None:
            ind = data[0].index("Alumno")
            for i in range(len(data)):
                data[i].remove(data[i][ind])
        if fecha == None:
            ind = data[0].index("Fecha")
            for i in range(len(data)):
                data[i].remove(data[i][ind])
        if hora == None:
            ind = data[0].index("Hora")
            for i in range(len(data)):
                data[i].remove(data[i][ind])
        if tema == None:
            ind = data[0].index("Tema")
            for i in range(len(data)):
                data[i].remove(data[i][ind])
        if notas == None:
            ind = data[0].index("Notas")
            for i in range(len(data)):
                data[i].remove(data[i][ind]) 

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
        contenido += f"Alumno: {tutoria.alumno.first_name} {tutoria.alumno.last_name} {tutoria.alumno.second_last_name}\n"
        contenido += f"Tutor: {tutoria.tutor.first_name} {tutoria.tutor.last_name} {tutoria.tutor.second_last_name}\n"
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
        # rol = self.request.user.get_rol()
        if self.request.user.has_role("TUT"):
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

        # rol = self.request.user.has_role("ALU")
        if self.request.user.has_role("ALU"):
            recipient = Tutor.objects.get(pk=alumno.tutor_asignado)

        # notify.send(alumno, recipient=recipient, verb='Nueva solicitud de tutoria', description=f'{form.instance.get_tema_display()}')
        # Eliminar corchetes de la lista
        notify.send(alumno, recipient=recipient, verb='Nueva solicitud de tutoria', description=f'{", ".join(form.instance.get_tema_display())}')
        
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
    
# Carta de notificación de tutorados (para el tutor)
class ReporteCreateView(CodaViewMixin, CreateView):
    model = Coda
    form_class = FormReporte
    template_name = 'Tutorias/generartutorados.html'
    success_url = reverse_lazy('Tutorados-Coda')  # Cambia esto a la URL adecuada

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tutor_pk = self.kwargs.get('pk')
        tutor_instance = Tutor.objects.get(pk=tutor_pk)
        kwargs['tutor_instance'] = tutor_instance
        return kwargs

    def form_valid(self, form):
        # Obtén el nombre del alumno desde la URL
        tutor_pk = self.kwargs.get('pk_tutor')

        # Busca el alumno por nombre
        tutor = get_object_or_404(Tutor, pk=tutor_pk)

        # Completa el formulario con los datos del alumno
        form.instance.tutor = tutor

        return super().form_valid(form)
    
    def paragraph_replace_text(self,paragraph, regex, replace_str):
        while True:
            text = paragraph.text
            match = regex.search(text)
            if not match:
                break

            # --- when there's a match, we need to modify run.text for each run that
            # --- contains any part of the match-string.
            runs = iter(paragraph.runs)
            start, end = match.start(), match.end()

            # --- Skip over any leading runs that do not contain the match ---
            for run in runs:
                run_len = len(run.text)
                if start < run_len:
                    break
                start, end = start - run_len, end - run_len

            # --- Match starts somewhere in the current run. Replace match-str prefix
            # --- occurring in this run with entire replacement str.
            run_text = run.text
            run_len = len(run_text)
            run.text = "%s%s%s" % (run_text[:start], replace_str, run_text[end:])
            end -= run_len  # --- note this is run-len before replacement ---

            # --- Remove any suffix of match word that occurs in following runs. Note that
            # --- such a suffix will always begin at the first character of the run. Also
            # --- note a suffix can span one or more entire following runs.
            for run in runs:  # --- next and remaining runs, uses same iterator ---
                if end <= 0:
                    break
                run_text = run.text
                run_len = len(run_text)
                run.text = run_text[end:]
                end -= run_len

        # --- optionally get rid of any "spanned" runs that are now empty. This
        # --- could potentially delete things like inline pictures, so use your judgement.
        # for run in paragraph.runs:
        #     if run.text == "":
        #         r = run._r
        #         r.getparent().remove(r)

        return paragraph

    def post(self, request,pk):
        form = request.POST
        oficio_form = form.get('oficio')
        plantilla_nombre = form.get('plantilla')
        fecha_form = form.get('fecha')
        fecha_form = datetime.strptime(fecha_form,'%Y-%m-%dT%H:%M').date()
        tutor_pk = self.kwargs.get('pk')
        
        plantilla = get_object_or_404(Documento, nombre=plantilla_nombre)
        tutor = get_object_or_404(Tutor, pk=tutor_pk)
        open_plantilla = docx.Document(plantilla.archivo)   

        # Verifica si el archivo tiene tablas
        if not open_plantilla.tables:
            messages.error(request, "Este archivo no es compatible con el tipo de carta que deseas generar")
            return redirect('Reporte-create', pk=pk)

        #Creación de las expresiones regulares que se buscaran en el doc
        reg_placeh = re.compile(r'\{.*?\}') #Placeholder "{}"
        reg_ofi = re.compile(r'\{no_oficio\}') #Número de oficio
        reg_fech =re.compile( r'\{fecha\}') #Fecha
        reg_tut = re.compile(r'\{nombre_mayus_tutor\}') #Nombre de tutor en mayusculas
        reg_est = re.compile(r'\{estimado\}') # indentificamos el articulo en minusculas
        reg_tut_min = re.compile(r'\{nombre_tutor\}')
        reg_lic = re.compile(r'\{licenciatura\}')

        tut_alums = Alumno.objects.filter(tutor_asignado=tutor_pk)
        
        ## EDICIÓN DE LA TABLA
        # Find the table you want to replace (assuming it's the first table)
        old_table = open_plantilla.tables[0]
        
        # Extract headers from the first row
        headers = [cell.text for cell in old_table.rows[0].cells]
        
        # Extract table style
        table_style = old_table.style

        # Find the parent element of the table (usually a paragraph)
        parent = old_table._element.getparent()

        # Insert a placeholder before removing the old table
        placeholder = open_plantilla.add_paragraph()
        parent.insert(parent.index(old_table._element), placeholder._element)

        # Remove the old table
        parent.remove(old_table._element)

        # Insert the new table at the placeholder position
        new_table = open_plantilla.add_table(rows=1, cols=len(headers))
        new_table.style = table_style
        placeholder._element.addnext(new_table._element)
        
        # Extract column widths
        column_widths = [cell.width for cell in old_table.rows[0].cells]

        # Apply column widths
        for i, width in enumerate(column_widths):
            new_table.columns[i].width = width

        # Populate headers
        header_cells = new_table.rows[0].cells
        for i, header in enumerate(headers):
            header_cells[i].text = header
            header_cells[i]._element.get_or_add_tcPr().append(
                docx.oxml.parse_xml(r'<w:shd {} w:fill="BFBFBF"/>'.format(docx.oxml.ns.nsdecls('w')))
            )

        # Copy paragraph styles and cell formatting from old headers
        for i, old_cell in enumerate(old_table.rows[0].cells):
            new_cell = new_table.rows[0].cells[i]
            new_cell.paragraphs[0].style = old_cell.paragraphs[0].style
            new_cell._element.get_or_add_tcPr().extend(old_cell._element.get_or_add_tcPr())

        # Populate the new table with filtered data
        for obj in tut_alums:
            # apellidos = re.findall(r'[A-Z][a-z]*', obj.last_name)
            # apellidos = re.findall(r'[A-Z][a-z]*', obj.last_name)
            # apellidos = re.findall(r'[A-Z][a-z]*', obj.last_name) + [''] * (2 - len(re.findall(r'[A-Z][a-z]*', obj.last_name)))
            row_cells = new_table.add_row().cells
            row_cells[0].text = str(obj.trimestre_ingreso)  # Replace with actual fields
            row_cells[1].text = str(obj.matricula)  # Replace with actual fields
            # row_cells[2].text = str(obj.last_name)
            row_cells[2].text = str(obj.last_name) #Si el modelo tiene un campo para segundo apellido, agregar
            row_cells[3].text = str(obj.second_last_name) #Si el modelo tiene un campo para segundo apellido, agregar
            row_cells[4].text = str(obj.first_name)  # Replace with actual fields
        
        # Ensure data rows inherit cell formatting from old table
        for row_index, row in enumerate(new_table.rows[1:]):
            old_row = old_table.rows[min(row_index + 1, len(old_table.rows) - 1)]  # Avoid index out of bounds
            for cell_index, cell in enumerate(row.cells):
                old_cell = old_row.cells[cell_index]
                cell.paragraphs[0].style = old_cell.paragraphs[0].style
                cell._element.get_or_add_tcPr().extend(old_cell._element.get_or_add_tcPr())

        # Antes del ciclo for p in open_plantilla.paragraphs:
        self.est = ""
        self.dr = ""
        self.name = ""
        self.name = f"{tutor.first_name} {tutor.last_name}"
        self.nombre_licenciatura = ""
        if tutor.sexo == "M":
            # print(f'Masculino')
            self.est = "Estimado"
            self.dr = "Dr."
        if tutor.sexo == "F":
            self.est = "Estimada"
            self.dr = "Dra."
        if tutor.second_last_name:
            self.name = self.name + f" {tutor.second_last_name}"

        carreras_dict = {
            "MAT": "Matemáticas Aplicadas",
            "COM": "Ingeniería en Computación",
            "IB": "Ingeniería Biológica",
            "BM": "Biología Molecular"
        }
        self.nombre_licenciatura = carreras_dict.get(tutor.coordinacion, "Licenciatura desconocida")

        ##EDICIÓN DE LOS PLACEHOLDERS
        c=0
        for p in open_plantilla.paragraphs:
            c = c+1
            # print(c)
            line = p.text
            result = []
            line_matches = [] if (result := re.findall(reg_placeh,line)) is None else result
            # print(f'Before cycle: {(line_matches)}') if line_matches else None 

            for match in line_matches:
                print(f'Esta linea: {match} hizo match')
                if re.search(reg_ofi,match):
                    self.paragraph_replace_text(p, reg_ofi, f"{oficio_form}").text
                if re.match(reg_fech,match):
                    self.paragraph_replace_text(p, reg_fech, f"{fecha_form}").text
                if re.match(reg_tut,match):
                    print(f'IF de tutor')
                    print(f'Sexo: {tutor.sexo}')
                    self.paragraph_replace_text(p, reg_tut,(self.dr+" "+self.name).upper()).text
                if re.match(reg_est,match):
                    self.paragraph_replace_text(p, reg_est, self.est)
                if re.match(reg_tut_min,match):
                    self.paragraph_replace_text(p, reg_tut_min, self.dr+" "+self.name)
                if re.match(reg_lic, match):
                    self.paragraph_replace_text(p,reg_lic, self.nombre_licenciatura)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename={tutor.last_name}_TUTORES_ATENDIDOS.docx'
        
        open_plantilla.save(response)
        
        return response
        # return FileResponse(buffer, as_attachment=True, filename=f'{tutor.last_name.upper()}_TUTORES_ATENDIDOS_21-24.pdf')
        # return super().post(request)

# Carta de asignación tutor para alumno (para el alumno)
class Reporte2CreateView(CodaViewMixin, CreateView):
    model = Coda
    form_class = FormReporte
    template_name = 'Tutorias/generarnotiftutor.html'
    success_url = reverse_lazy('Tutorados-Coda')  # Cambia esto a la URL adecuada

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get selected students from URL parameters
        selected_ids = self.request.GET.getlist('selected_alumnos')
        print(selected_ids)
        
        # Fetch student objects from the database
        alumnos = get_list_or_404(Alumno, pk__in=selected_ids)

        # Pass single or multiple students to template
        context['alumnos'] = alumnos
        context['is_multiple'] = len(alumnos) > 1  # True if multiple students

        return context

    def form_valid(self, form):
        # Obtén el nombre del alumno desde la URL
        tutor_pk = self.kwargs.get('pk_tutor')

        # Busca el alumno por nombre
        tutor = get_object_or_404(Tutor, pk=tutor_pk)

        # Completa el formulario con los datos del alumno
        form.instance.tutor = tutor

        return super().form_valid(form)
    
    def paragraph_replace_text(self,paragraph, regex, replace_str):
        while True:
            text = paragraph.text
            match = regex.search(text)
            if not match:
                break

            # --- when there's a match, we need to modify run.text for each run that
            # --- contains any part of the match-string.
            runs = iter(paragraph.runs)
            start, end = match.start(), match.end()

            # --- Skip over any leading runs that do not contain the match ---
            for run in runs:
                run_len = len(run.text)
                if start < run_len:
                    break
                start, end = start - run_len, end - run_len

            # --- Match starts somewhere in the current run. Replace match-str prefix
            # --- occurring in this run with entire replacement str.
            run_text = run.text
            run_len = len(run_text)
            run.text = "%s%s%s" % (run_text[:start], replace_str, run_text[end:])
            end -= run_len  # --- note this is run-len before replacement ---

            # --- Remove any suffix of match word that occurs in following runs. Note that
            # --- such a suffix will always begin at the first character of the run. Also
            # --- note a suffix can span one or more entire following runs.
            for run in runs:  # --- next and remaining runs, uses same iterator ---
                if end <= 0:
                    break
                run_text = run.text
                run_len = len(run_text)
                run.text = run_text[end:]
                end -= run_len

        # --- optionally get rid of any "spanned" runs that are now empty. This
        # --- could potentially delete things like inline pictures, so use your judgement.
        # for run in paragraph.runs:
        #     if run.text == "":
        #         r = run._r
        #         r.getparent().remove(r)

        return paragraph

    def post (self, request, pk):
        selected_ids = self.request.GET.getlist('selected_alumnos')

        form = request.POST
        oficio_form = form.get('oficio')
        plantilla_nombre = form.get('plantilla')
        fecha_form = form.get('fecha')
        fecha_form = datetime.strptime(fecha_form,'%Y-%m-%dT%H:%M').date()
        tutor_pk = self.kwargs.get('pk')
        alumnos = get_list_or_404(Alumno, pk__in=selected_ids)
        plantilla = get_object_or_404(Documento, nombre=plantilla_nombre)
        tutor = get_object_or_404(Tutor, pk=tutor_pk)
        
        #Creación de las expresiones regulares que se buscaran en el doc
        reg_placeh = re.compile(r'\{.*?\}') #Placeholder "{}"
        reg_gen = re.compile(r'\{(a|o|e)\}') #Género
        # reg_tut = re.compile(r'\{(Dr\.|Dra\.|Doctor|Doctora)\s+(.)*\}')
        # reg_tut = re.compile(r'\{(((d|D)[a-zA-Z]+)(\.*))+(\s[A-Z][a-zA-Z]*)*(\s[A-Z][a-zA-Z]*)+(\s[A-Z][a-zA-Z]*)*\}') #Tutor ex. Dr/doctor Algo
        reg_palab_tutor = re.compile(r'\{(T|t)utor(a)*\}')
        reg_tut = re.compile(r'\{(((d|D)[a-zA-Z]+)(\.*))+\s+(.)*\}') #Tutor ex. Dr/doctor Algo
        reg_fech =re.compile( r'\{[0-9]+.*[a-zA-Z0-9]+.*[0-9]+\}') #Fecha
        reg_ofi = re.compile(r'\{[a-zA-Z0-9\-]*(_[a-zA-Z0-9]*)+\}') #Número de oficio
        reg_alu = re.compile(r'\{(?!LICENCIATURA|LIC.|Licenciatura|Lic.)(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*\.?|[A-ZÁÉÍÓÚÑ]+\.?)(?:\s+(?:de|del|la|y|los|las|san|santa|C|Dr|Dra|Lic|Ing|Sr|Sra)\.?|[A-ZÁÉÍÓÚÑ]+\.?)*\s+(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*|[A-ZÁÉÍÓÚÑ]+)\b(?:\s+(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*|[A-ZÁÉÍÓÚÑ]+))*\}')
        reg_carr = re.compile(r'\{(LICENCIATURA|LIC.|Licenciatura|Lic.)(.)*\}')
        reg_det = re.compile(r'\{(la|el|él)\}')

        ##EDICIÓN DE LOS PLACEHOLDERS
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for alumno in alumnos:
                open_plantilla = docx.Document(plantilla.archivo)
                c=0
                for p in open_plantilla.paragraphs:
                    c = c+1
                    # print(c)
                    line = p.text
                    result = []
                    line_matches = [] if (result := re.findall(reg_placeh,line)) is None else result
                    for match in line_matches:
                        if re.search(reg_ofi,match):
                            self.paragraph_replace_text(p, reg_ofi, f"{oficio_form}").text
                        if re.match(reg_fech,match):
                            self.paragraph_replace_text(p, reg_fech, f"{fecha_form}").text
                        # if re.match(reg_tut,match):
                        #     print(f"Tutor IF")
                        #     self.paragraph_replace_text(p, reg_tut, f"Doctor {tutor.last_name}").text
                        if re.match(reg_palab_tutor,match):
                            if tutor.sexo == "M":
                                self.paragraph_replace_text(p, reg_palab_tutor, f"tutor").text
                            if tutor.sexo == "F":
                                self.paragraph_replace_text(p, reg_palab_tutor, f"tutora").text
                        if re.match(reg_tut,match):
                            if tutor.sexo == "M":
                                self.paragraph_replace_text(p, reg_tut, f"Dr. {tutor.last_name}").text
                            if tutor.sexo == "F":
                                self.paragraph_replace_text(p, reg_tut, f"Dra. {tutor.last_name}").text
                        if re.match(reg_alu,match):
                            self.paragraph_replace_text(p, reg_alu, f"{alumno.first_name} {alumno.last_name}").text
                        if re.match(reg_carr,match):
                            self.paragraph_replace_text(p, reg_carr, f"{alumno.get_carrera_display()}").text
                        if re.match(reg_det,match):
                            if tutor.sexo == "M":
                                self.paragraph_replace_text(p, reg_det, f"él").text
                            if tutor.sexo == "F":
                                self.paragraph_replace_text(p, reg_det, f"la").text
                        if re.match(reg_gen,match):
                            if tutor.sexo == "M":
                                self.paragraph_replace_text(p, reg_gen, f"o").text
                            if tutor.sexo == "F":
                                self.paragraph_replace_text(p, reg_gen, f"a").text

                # Save each document to ZIP
                temp_buffer = BytesIO()
                open_plantilla.save(temp_buffer)
                temp_buffer.seek(0)
                zip_file.writestr(f"{alumno.first_name}_{alumno.last_name}_TUTOR.docx", temp_buffer.getvalue())

        # Return ZIP file
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="Documentos_Alumnos.zip"'

        return response


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

class VerAlumnosListView(CodaViewMixin, ListView):
    model = Alumno
    template_name = 'Tutorias/verAlumnos_coda.html'

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
        print(context)
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
        
        
        # rol = self.request.user.get_rol()
        if self.request.user.has_role("ALU"):
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


class RealizarSeguimientoView(TutorViewMixin, UpdateView):
    model = Tutoria
    form_class = FormSeguimiento
    template_name = 'Tutorias/seguimientoTutoria.html'
    success_url =  reverse_lazy('Tutorias-historial')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        tutor = Tutor.objects.get(pk=self.request.user)
        recipient = Alumno.objects.filter(pk=self.get_object().alumno)

        notify.send(tutor, recipient=recipient, verb='Seguimiento de tutoria realizado')
        return super().form_valid(form)
