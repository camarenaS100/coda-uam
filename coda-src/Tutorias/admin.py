from django.contrib import admin
from.models import Tutoria
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import CharWidget

# Register your models here.

class TutoriaResource(resources.ModelResource):
    tema_display = fields.Field(column_name='tema', attribute='tema', widget=CharWidget())

    class Meta:
        model = Tutoria
        fields = ('id', 'tema_display', 'alumno', 'tutor', 'descripcion', 'fecha')
    
    def dehydrate_tema_display(self, tutoria):
        return tutoria.get_tema_display()


class TutoriasAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """Define admin model for Tutoria objects"""

    resource_class = TutoriaResource

    list_display = ('tema', 'alumno', 'tutor', 'descripcion', 'fecha')
    search_fields = ('tema', 'alumno', 'tutor', 'fecha')

admin.site.register(Tutoria, TutoriasAdmin)