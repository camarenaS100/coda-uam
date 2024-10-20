
BECAS = "BEC"
INSCRIPCION = "INS"
INGLES = "ING"
COLEGIADO = "ORG"
REGLAMENTOS = "REG"
SERVICIO = "SS"
MOVILIDAD = "MOV"
PROYECTO = "PT"
ESTANCIA = "EV" 
TRAYECTORIA = "TC"
GRUPO = "EG" 
TITULACION = "TIT"
EGRESO = "EGRE"
PERSONALES = "PER"
SEGUIMIENTO = "SR"
OTRO = "OTRO"

TEMAS = [
    (BECAS, "Becas"),
    (INSCRIPCION, "Inscripción"),
    (INGLES, "Inglés"),
    (COLEGIADO, "Órgano colegiado"),
    (REGLAMENTOS, "Reglamentos"),
    (SERVICIO, "Servicio Social"),
    (MOVILIDAD, "Movilidad"),
    (PROYECTO, "Proyecto Terminal"),
    (ESTANCIA, "Estancia de Verano"),
    (TRAYECTORIA, "Trayectoria Curricular"),
    (GRUPO, "Eleccion de grupo"),
    (TITULACION, "Titulación"),
    (EGRESO, "Egreso"),
    (PERSONALES, "Personales"),
    (SEGUIMIENTO, "Seguimiento de reunión"),
    (OTRO, "Otro")
]

ACEPTADO = 'ACE'
RECHAZADO = 'REJ'
PENDIENTE = 'PEN'

ESTADO = [
    (ACEPTADO, 'Aceptada'),
    (RECHAZADO, 'Rechazada'),
    (PENDIENTE, 'Pendiente')
]

DURACION_ASESORIA = [
    (0, 'Menos de 30 minutos'),
    (1, '30 minutos'),
    (2, '1 hora'),
    (3, '2 horas'),
    (4, 'Más de dos horas')
]