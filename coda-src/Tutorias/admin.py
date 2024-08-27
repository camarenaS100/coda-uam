from django.contrib import admin
from.models import Tutoria
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.

class TutoriaResource(resources.ModelResource):
    class Meta:
        model = Tutoria
        fields = ('id', 'tema', 'alumno', 'tutor', 'descripcion', 'fecha')


class TutoriasAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """Define admin model for Tutoria objects"""

    resource_class = TutoriaResource

    list_display = ('tema', 'alumno', 'tutor', 'descripcion', 'fecha')
    search_fields = ('tema', 'alumno', 'tutor', 'fecha')

admin.site.register(Tutoria, TutoriasAdmin)