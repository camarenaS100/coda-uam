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

from django.views.generic.list import ListView
from django.http import HttpResponseBadRequest
from django.views.generic import View

from django.http import HttpResponse
#from .models import Tutoria

from . import forms as userForms
from .mixins import BaseAccessMixin, CodaViewMixin, AlumnoViewMixin, CordinadorViewMixin, TutorViewMixin


# TODO Remove test views
def login_view_test(request):

    return render(request, 'Usuarios/login.html')

def perfil_view_test(request):

    return render(request, 'Usuarios/perfil.html')

def recordarcontras_view_test(request):

    return render(request, 'Usuarios/recordarContrasenia.html')



class PerfilAlumnoView(BaseAccessMixin, DetailView):

    model = Alumno
    template_name = 'Usuarios/perfil_alumno.html'
    

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        return context

class PerfilTutorView(BaseAccessMixin, DetailView):

    model = Tutor
    template_name = 'Usuarios/perfil_tutor.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()

@login_required
def redirect_perfil(request):

    if Tutor.objects.filter(pk=request.user.pk).exists():
        return redirect('perfil-tutor', pk=request.user.pk)
    
    if Alumno.objects.filter(pk=request.user.pk).exists():
        return redirect('perfil-alumno', pk=request.user.pk)
    if Coda.objects.filter(pk=request.user.pk).exists():
        return redirect('perfil-coda', pk=request.user.pk)
    if Cordinador.objects.filter(pk=request.user.pk).exists():
        return redirect('perfil-cordinador', pk=request.user.pk)
    
    return redirect('perfil-alumno', pk=request.user.pk)

class PerfilCodaView(BaseAccessMixin, DetailView):

    model = Coda
    template_name = 'Usuarios/perfil_cooda.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()
    

class PerfilCordinadorView(BaseAccessMixin, DetailView):

    model = Cordinador
    template_name = 'Usuarios/perfil_cordinador.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset()

    

# TODO Eliminar para prod
# class DebugTutoriasView(LoginRequiredMixin, ListView):

#     model = Tutor
#     template_name='Tutorias/verTutorias_coordinador.html'

#     def get_queryset(self) -> QuerySet[Any]:
#         return super().get_queryset()
    

class UsuarioLoginView(LoginView):

    redirect_authenticated_user = True

    template_name = "Usuarios/login.html"
    
    def form_invalid(self, form: AuthenticationForm) -> HttpResponse:
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def login_success(request):
    """
    Redirecciona los usuarios a su view correspondiente
    """


    if Alumno.objects.filter(pk=request.user.pk).exists():
        return redirect('Tutorias-alumno')
    
    if Tutor.objects.filter(pk=request.user.pk).exists():
        return redirect('Tutorias-tutor')
    if Cordinador.objects.filter(pk=request.user.pk).exists():
        return redirect('Tutorias-Coordinacion')
    if Coda.objects.filter(pk=request.user.pk).exists():
        return redirect('Tutores-Coda')
    
    print('ERROR: Usuario no definido')
    return HttpResponseBadRequest("ERROR. Tipo de usuario o rol no definido")
    #return redirect()
    # if Usuario.objects.filter(pk=request.user.pk).exists:
    #     return redirect('Tutorias-coordinador')

class ChangePasswordView(BaseAccessMixin, PasswordChangeView):
    template_name = 'Usuarios/change_password.html'  # Create a template for password change form
    success_url = reverse_lazy('password_change_done')  # Redirect to this URL after a successful password change

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Add any additional context data if needed
        return context

class PasswordChangeDoneView(TemplateView):
    template_name = 'Usuarios/password_change_done.html'

class BorrarNotificaciones(View):
    def post(self, request):
        usuario = Usuario.objects.get(pk=self.request.user.pk)
        notificaciones = usuario.notifications.unread()
        notificaciones.mark_all_as_read()


        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# Conjunto de Views Para Agregar usuarios

#PermissionRequiredMixin
class CreateAlumnoView(CodaViewMixin, CreateView):

    template_name = 'Usuarios/agregar_alumno.html'
    success_url = reverse_lazy('Tutores-Coda')
    #model = Alumno
    form_class = userForms.FormAlumno

    def post(self, request):
        form = userForms.FormAlumno(request.POST)
        print(request)
        print(request.POST.get('tutor_asignado'))
        print("Info del form")
        print(form)
        if form.is_valid():
            print("Y es válida")
            form.save()
        return HttpResponseRedirect(request.path_info)

#PermissionRequiredMixin
class CreateCordinadorView(CodaViewMixin, CreateView):
    template_name = 'Usuarios/agregar_cordinador.html'
    success_url = reverse_lazy('Tutores-Coda')
    #model = Cordinador
    form_class = userForms.FormCordinador

    
#PermissionRequiredMixin
class CreateTutorView(CodaViewMixin, CreateView):
    template_name = 'Usuarios/agregar_tutor.html'
    success_url = reverse_lazy('Tutores-Coda')
    #model = Tutor
    form_class = userForms.FormTutor





# class AceptarTutoriaView(View):
#     def post(self, request, pk):
#         tutoria = get_object_or_404(Tutoria, pk=pk)
#         tutoria.estado = ACEPTADO
#         tutoria.save()
#         return redirect('Tutorias-tutor')  