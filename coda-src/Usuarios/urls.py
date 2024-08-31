from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from . import views
import notifications.urls

urlpatterns = [
    path('', views.UsuarioLoginView.as_view(), name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    #path('perfil-test/', views.perfil_view_test, name='perfil-test'),
    path('perfil-alumno/<int:pk>/', views.PerfilAlumnoView.as_view(), name='perfil-alumno'),
    path('perfil-tutor/<int:pk>/', views.PerfilTutorView.as_view(), name='perfil-tutor'),
    path('perfil-cordinador/<int:pk>/', views.PerfilCordinadorView.as_view(), name='perfil-cordinador'),
    path('perfil-coda/<int:pk>/', views.PerfilCodaView.as_view(), name='perfil-coda'),
    path('perfil/', views.redirect_perfil, name='perfil'),
    path('reset-password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    re_path(r'^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    re_path(r'login_success/$', views.login_success, name='login_success'),

    # Password change URLs
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password-change-done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('remove-notifications/', views.BorrarNotificaciones.as_view(), name='remove-notifications'),

    # URLs del Coda para creación de usuarios
    path('registrar-alumno/', views.CreateAlumnoView.as_view(), name='crear-alumno'),
    path('registrar-tutor/', views.CreateTutorView.as_view(), name='crear-tutor'),
    path('registrar-coordinador/', views.CreateCordinadorView.as_view(), name='crear-coordinador'),
    path('export-tutorias/<int:tutor_id>/', views.export_tutorias_to_xlsx, name='export_tutorias'),
    


    # ... (other existing URL patterns)
]