from django.contrib import admin
from.models import Tutoria
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import CharWidget

# Register your models here.

class TutoriaResource(resources.ModelResource):
    tema_display = fields.Field(column_name='tema', attribute='tema', widget=CharWidget())
    alumno_full_name = fields.Field(column_name='alumno_full_name')
    tutor_full_name = fields.Field(column_name='tutor_full_name')

    class Meta:
        model = Tutoria
        fields = ('id', 'tema_display', 'alumno_full_name', 'tutor_full_name', 'descripcion', 'fecha')

    def dehydrate_tema_display(self, tutoria):
        return tutoria.get_tema_display()

    def dehydrate_alumno_full_name(self, tutoria):
        return f"{tutoria.alumno.first_name} {tutoria.alumno.last_name}"

    def dehydrate_tutor_full_name(self, tutoria):
        return f"{tutoria.tutor.first_name} {tutoria.tutor.last_name}"



class TutoriasAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """Define admin model for Tutoria objects"""

    resource_class = TutoriaResource

    list_display = ('tema', 'alumno', 'tutor', 'descripcion', 'fecha')
    search_fields = ('tema', 'alumno', 'tutor', 'fecha')

admin.site.register(Tutoria, TutoriasAdmin)