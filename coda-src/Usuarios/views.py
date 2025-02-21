from typing import Any, Dict
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .models import Usuario, Tutor, Alumno, Coda, Cordinador
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import ImportAlumnosForm
from django.views.generic.list import ListView
from django.http import HttpResponseBadRequest
from django.views.generic import View
from django.http import HttpResponse
#from .models import Tutoria
from . import forms as userForms
from .mixins import BaseAccessMixin, CodaViewMixin, AlumnoViewMixin, CordinadorViewMixin, TutorViewMixin
from django.http import JsonResponse
from .forms import ImportAlumnosForm
from .models import Alumno, Usuario, Tutor
from .constants import CARRERAS, ESTADOS_ALUMNO, SEXOS, ALUMNO
from django.contrib.auth.hashers import make_password
import io
import pandas as pd


# Test Views (Remove for production)
def login_view_test(request):
    return render(request, 'Usuarios/login.html')

def perfil_view_test(request):
    return render(request, 'Usuarios/perfil.html')

def recordarcontras_view_test(request):
    return render(request, 'Usuarios/recordarContrasenia.html')


### Profile Views Updated for `Usuario`
class PerfilAlumnoView(BaseAccessMixin, DetailView):
    model = Usuario
    template_name = 'Usuarios/perfil_alumno.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Usuario.objects.filter(roles__contains=["ALU"])  # Filter for Alumnos


class PerfilTutorView(BaseAccessMixin, DetailView):
    model = Usuario
    template_name = 'Usuarios/perfil_tutor.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Usuario.objects.filter(roles__contains=["TUT"])  # Filter for Tutors


class PerfilCodaView(BaseAccessMixin, DetailView):
    model = Usuario
    template_name = 'Usuarios/perfil_cooda.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Usuario.objects.filter(roles__contains=["CODA"])  # Filter for Coda


class PerfilCordinadorView(BaseAccessMixin, DetailView):
    model = Usuario
    template_name = 'Usuarios/perfil_cordinador.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Usuario.objects.filter(roles__contains=["COR"])  # Filter for Coordinadores


### Role-Based Profile Redirection
@login_required
def redirect_perfil(request):
    user = request.user

    if user.has_role("TUT"):
        return redirect('perfil-tutor', pk=user.pk)

    if user.has_role("ALU"):
        return redirect('perfil-alumno', pk=user.pk)

    if user.has_role("CODA"):
        return redirect('perfil-coda', pk=user.pk)

    if user.has_role("COR"):
        return redirect('perfil-cordinador', pk=user.pk)

    return redirect('perfil-alumno', pk=user.pk)  # Default case


### Role-Based Login Success Redirection
@login_required
def login_success(request):
    user = request.user
    selected_role = request.session.get("role")  # Retrieve stored role from session

    if selected_role == "alumno" and user.has_role("ALU"):
        return redirect("Tutorias-alumno")

    if selected_role == "tutor" and user.has_role("TUT"):
        return redirect("Tutorias-tutor")

    if selected_role == "coordinador" and user.has_role("COR"):
        return redirect("Tutorias-Coordinacion")

    if selected_role == "coda" and user.has_role("CODA"):
        return redirect("Tutores-Coda")

    print("ERROR: Usuario no definido o rol incorrecto")
    return HttpResponseBadRequest("ERROR. Tipo de usuario o rol no definido")


### User Authentication Views
class UsuarioLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = "Usuarios/login.html"

    def form_valid(self, form):
        """
        If the form is valid, log in the user and store the selected role in session.
        """
        response = super().form_valid(form)  # Perform default login process
        role = self.request.POST.get("role")  # Get selected role from the login form
        if role:
            self.request.session["role"] = role  # Store the role in session
        return response  # Proceed with normal redirection


class ChangePasswordView(BaseAccessMixin, PasswordChangeView):
    template_name = 'Usuarios/change_password.html'  # Create a template for password change form
    success_url = reverse_lazy('password_change_done')  # Redirect to this URL after a successful password change

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)


class PasswordChangeDoneView(TemplateView):
    template_name = 'Usuarios/password_change_done.html'


### Notification Handling
class BorrarNotificaciones(View):
    def post(self, request):
        usuario = Usuario.objects.get(pk=self.request.user.pk)
        notificaciones = usuario.notifications.unread()
        notificaciones.mark_all_as_read()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


### Create User Views (Updated for `Usuario`)
class CreateAlumnoView(CodaViewMixin, CreateView):
    template_name = 'Usuarios/agregar_alumno.html'
    success_url = reverse_lazy('Tutores-Coda')
    form_class = userForms.FormAlumno


class CreateCordinadorView(CodaViewMixin, CreateView):
    template_name = 'Usuarios/agregar_cordinador.html'
    success_url = reverse_lazy('Tutores-Coda')
    form_class = userForms.FormCordinador


class CreateTutorView(CodaViewMixin, CreateView):
    template_name = 'Usuarios/agregar_tutor.html'
    success_url = reverse_lazy('Tutores-Coda')
    form_class = userForms.FormTutor


class ImportAlumnosView(CodaViewMixin, FormView):
    template_name = "Usuarios/importar_alumnos.html"
    form_class = userForms.ImportAlumnosForm
    success_url = reverse_lazy('Tutores-Coda')

    def form_valid(self, form):
        uploaded_file = self.request.FILES.get('archivo')

        # Get default context (ensures user roles are included)
        context = self.get_context_data(form=form)

        if not uploaded_file:
            context["error"] = "No file uploaded."
            return render(self.request, self.template_name, context)

        warnings = []  # Stores students that couldn't be created
        success_count = 0  # Tracks successful imports

        try:
            file_extension = uploaded_file.name.split(".")[-1]
            if file_extension in ["xls", "xlsx"]:
                df = pd.read_excel(uploaded_file)
            elif file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            else:
                context["error"] = "Invalid file format."
                return render(self.request, self.template_name, context)

            # Check for required columns
            required_columns = ["Plan de estudios", "Matrícula", "Correo institucional", "Correo", "Apellido 1", "Apellido 2", "Nombres", "No. Económico", "Estado", "Sexo"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                context["error"] = f"Missing columns: {', '.join(missing_columns)}"
                return render(self.request, self.template_name, context)

            # Process data row by row
            for _, row in df.iterrows():
                try:
                    matricula = str(row["Matrícula"]).strip()
                    email = row["Correo institucional"].strip()
                    correo_personal = row["Correo"].strip()
                    last_name = f"{row['Apellido 1']} {row['Apellido 2']}".strip()
                    first_name = row["Nombres"].strip()
                    carrera = next((key for key, value in CARRERAS if value == row["Plan de estudios"]), None)
                    estado = next((key for key, value in ESTADOS_ALUMNO if value == row["Estado"]), None)
                    sexo = next((key for key, value in SEXOS if value == row["Sexo"]), None)
                    tutor_id = row["No. Económico"]

                    # Ensure required fields are valid
                    if not (matricula and email and first_name and last_name and carrera and estado and sexo):
                        warnings.append(f"Alumno {matricula}: Datos obligatorios faltantes.")
                        continue  # Skip to the next student

                    # Find assigned tutor
                    tutor_asignado = Tutor.objects.filter(matricula=tutor_id).first()
                    if not tutor_asignado:
                        warnings.append(f"Alumno {matricula}: Tutor con ID {tutor_id} no encontrado.")
                        continue

                    # Generate password (increment each digit of matricula by 1)
                    password = "".join(str(int(digit) + 1) if digit.isdigit() else digit for digit in matricula)
                    hashed_password = make_password(password)

                    # Create Usuario
                    usuario, created = Usuario.objects.get_or_create(
                        matricula=matricula,
                        defaults={
                            "email": email,
                            "correo_personal": correo_personal,
                            "first_name": first_name,
                            "last_name": last_name,
                            "password": hashed_password,
                            "rol": [ALUMNO],
                        },
                    )

                    # Check if already an Alumno
                    if not Alumno.objects.filter(id=usuario.id).exists():
                        alumno = Alumno(
                            id=usuario.id,
                            carrera=carrera,
                            estado=estado,
                            sexo=sexo,
                            tutor_asignado=tutor_asignado,
                        )
                        alumno.__dict__.update(usuario.__dict__)  # Copy fields
                        alumno.save()

                    success_count += 1  # Increment success counter

                except Exception as e:
                    warnings.append(f"Alumno {matricula}: {str(e)}")
                    continue  # Skip to next student

            # Update context
            context.update({
                "warnings": warnings if warnings else None,
                "success": f"{success_count} alumnos importados exitosamente." if success_count > 0 else None,
            })

            return render(self.request, self.template_name, context)

        except Exception as e:
            context.update({
                "error": str(e),
                "warnings": warnings if warnings else None,  # Ensure warnings are included
            })
            return render(self.request, self.template_name, context)



# class AceptarTutoriaView(View):
#     def post(self, request, pk):
#         tutoria = get_object_or_404(Tutoria, pk=pk)
#         tutoria.estado = ACEPTADO
#         tutoria.save()
#         return redirect('Tutorias-tutor')  