# Implementación de seguimiento de tutorías


## Funcionamiento general
Esta función es accesible desde la vista "Historial de tutorías" que puede ver el tutor. 

En la tabla que muestra el historial, se agrega una columna llamada "Seguimiento", y se agrega un botón a cada fila.


Al presionar este botón, se lleva formulario de seguimiento. El formulario de seguimiento muestra la información de la tutoría seleccionada, junto con el formulario a responder por el tutor.


Al envíar el formulario, se actualiza la fila en la tabla de tutorías

## Información que requiere el formulario

1. ¿El alumno asistió a la tutoría? (Si/No)

--- Las siguientes preguntas se activan sólo si se respondió "Sí" a la pregunta anterior ---

2. Duración de la tutoría (menos 30 min/30 min/1 hora/2 horas/más de 2 horas)
3. ¿Se firmó algún formato de solicitud de beca? (Sí/No)

--- La pregunta 4 solo se activa si se responde "Sí" a la pregunta anterior---

4. Nombre de la beca que se otorgó al alumno (respuesta libre)
5. ¿El alumno requirió asesoría especializada? (Sí/No)
6. Aspectos tratados en la tutoría, acuerdos o acciones establecidos, canalizaciones (respuesta libre)
7. ¿Nivel de impacto de tutoría en desempeño académico de alumno/a? (Selección del 1 al 5)
8. Resultados de tutoría (Respuesta libre)

## Modificaciones al código existente

* Se añadió la siguiente información a `models.py`:
```
    asistencia = models.BooleanField(default=False, blank=True, null=True)
    duracion = models.IntegerField(default=0, blank=True, null=True)
    firma_documentos_beca = models.BooleanField(default=False, blank=True, null=True)
    beca_otorgada = models.CharField(max_length=255, blank=True, null=True)
    asesoria_especializada = models.BooleanField(default=False, blank=True, null=True)
    observaciones = models.CharField(max_length=1000, blank=True, null=True)
    impacto_tutoria = models.IntegerField(default=0, blank=True, null=True)
    resultados_tutoria = models.CharField(max_length=1000, blank=True, null=True)
```
que representan los campos que se requieren para contener la información del seguimiento.

* Se añadió a `forms.py` el formato del formulario para validación (aunque no se usa al momento)
* Se añadió a `constants.py` las opciones que aparecen en el combobox para la selección de la duración de la tutoría
* Se modificó el template `historialtutoria.html` para agregar la nueva columna y el botón para abrir el formulario
* Se creó el template `seguimientoTutoria.html` que incluye todo el formulario del seguimiento
* Se añadió el url del template anterior en `url.py`
* Se creó la función `RealizarSeguimientoView` en `views.py` que maneja todo el backend de esta característica

## Flujo de ejecución
1. Tutor abre historial de tutorías
2. Tutor hace click en botón "Realizar seguimiento" asociado a una tutoría
3. Página de historial de tutorías manda información de tutoría seleccionada a página de seguimiento (en este caso, se usa la llave primaria de la tutoria)
4. Tutor llena formulario de seguimiento
5. Por medio de un post se manda la información a la función RealizarSeguimientoView y desde ahí se actualiza la tutoría