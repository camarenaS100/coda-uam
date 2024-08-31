from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    # path("vertutorias/", views.ver_tutorias),
    # path("editartutoria/", views.editar_tutoria),
    # path("solicitudtutoria/", views.solicitud_tutoria),
    #path('', views.index, name='index'),
    path('tutorias/<int:pk>/', views.TutoriasDetailView.as_view(), name='Tutorias-detail'),
    path('editar-tutoria/<int:pk>', views.TutoriaUpdateView.as_view(), name='Tutorias-update'),
    path('crear-tutoria/', views.TutoriaCreateView.as_view(), name='Tutorias-create'),
    
    #path('reset-password/', views.DebugTutoriasView.as_view(), name='reset_password'),
    
    # URLS COORDINADORESs
    path("tutores-cord/", views.VerTutoresCoordListView.as_view(), name="Tutores-Cordinador"),
    path('tutorias-coordinador/', views.VerTutoriasCoordinadorListView.as_view(), name='Tutorias-Coordinacion'),
    path('tutorias-coordinador/<int:pk>', views.VerTutoriasCoordinadorPorTutorListView.as_view(), name='Tutorias-Cordinador'),
    path('tutorados-coordinador/<int:pk>', views.VerTutoradosCoordinadorListView.as_view(), name='Tutorados-Cordinador'),


    # URLS ALUMNOS
    path('tutorias-alumno/', views.VerTutoriasAlumnoListView.as_view(), name='Tutorias-alumno'),
    path('tutoria-rapida/', views.QuickCreateTutoriaView.as_view(), name='tutoria-rapida'),

    # URLS TUTORES
    path('tutoria/<int:pk>/aceptar/', views.AceptarTutoriaView.as_view(), name='aceptar_tutoria'),
    path('tutoria/<int:pk>/rechazar/', views.RechazarTutoriaView.as_view(), name='rechazar_tutoria'),
    path('historial-tutorias/', views.HistorialTutoriasListView.as_view(), name='Tutorias-historial'),
    path('historial-tutorias-generar/', views.HistorialTutoriasGenerateView.as_view(), name='Tutorias-historial-generar'),
    path('tutorados-tutor/', views.VerTutoradosTutorListView.as_view(), name='Tutorados-tutor'),
    path('tutorias-tutor/', views.VerTutoriasTutorListView.as_view(),name='Tutorias-tutor'),
    path('crear-tutoria/<int:pk_alumno>/', views.CrearTutoriaPorAlumnoView.as_view(), name='crear-tutoria'),
     path('export-tutorias/<int:tutor_id>/', views.export_tutorias_to_xlsx, name='export_tutorias'),
    # URLS CODA 
    path('tutores-coda/', views.VerTutoresListView.as_view(), name='Tutores-Coda'),
    path('tutorias-coda/<int:pk>', views.VerTutoriasCodaListView.as_view(), name='Tutorias-Coda'),
    path('tutorados-coda/<int:pk>', views.VerTutoradosCodaListView.as_view(), name='Tutorados-Coda'),


    path('ruta-pdf/', views.generar_pdf, name='generar_pdf'),
    path('generar-txt/<int:pk>', views.generar_archivo_txt, name='generar_txt'),
    #path('debug-tutorias/', views.DebugTutoriasView.as_view(), name='debug-tutorias'),
    path('qr-code/', views.QRCodeView.as_view(), name='qr-code'),
    # Desactivamos la tutoria por tutor mientras se arregla la coordinacion de horarios
    #path('creartutoria/<int:pk_alumno>/', views.CrearTutoriaPorAlumnoView.as_view(),name='crear-tutoria-por-alumno'),
]