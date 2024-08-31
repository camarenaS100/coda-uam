from typing import Any, Dict
from .constants import TUTOR, ALUMNO, COORDINADOR, CODA, TEMPLATES
from .models import Usuario
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ContextConRolesMixin:

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_rol = self.request.user.get_rol()
        if user_rol == ALUMNO:
            context["header_footer"] = TEMPLATES[ALUMNO]
        elif user_rol == TUTOR:
            context["header_footer"] = TEMPLATES[TUTOR]
        elif user_rol == COORDINADOR:
            context["header_footer"] = TEMPLATES[COORDINADOR]
        elif user_rol == CODA:
            context["header_footer"] = TEMPLATES[CODA]
        print(context)
        return context

class ContextNotificationsMixin:

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = Usuario.objects.get(pk=self.request.user.pk)
        notifications_raw = user.notifications.unread()
        unread_notifications = []

        for notification in notifications_raw:
            notificacion_temp = {}
            notificacion_temp["header"] =  "Notificacion" if not notification.description else f"{notification.description}"
            notificacion_temp["text"] = f'{notification.verb} por {Usuario.objects.get(matricula=notification.actor).get_full_name()}'
            
            notificacion_temp["time"] = notification.timestamp
            #remitente = 
            #notificacion_temp["origen"] = f'{}'
            unread_notifications.append(notificacion_temp)
            

       
        context["notificaciones_list"] = unread_notifications
        return context
    
class BaseAccessMixin(LoginRequiredMixin, ContextConRolesMixin, ContextNotificationsMixin):

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)
    
class CodaViewMixin(BaseAccessMixin, UserPassesTestMixin):


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)
    
    def test_func(self) -> bool:
        return self.request.user.get_rol()==CODA
    
class TutorViewMixin(BaseAccessMixin, UserPassesTestMixin):


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)
    
    def test_func(self) -> bool:
        return self.request.user.get_rol()==TUTOR
    
class AlumnoViewMixin(BaseAccessMixin, UserPassesTestMixin):


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)
    
    def test_func(self) -> bool:
        return self.request.user.get_rol()==ALUMNO
    
class CordinadorViewMixin(BaseAccessMixin, UserPassesTestMixin):


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)
    
    def test_func(self) -> bool:
        return self.request.user.get_rol()==COORDINADOR