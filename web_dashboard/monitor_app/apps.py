import os
from django.apps import AppConfig

class MonitorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor_app'

    def ready(self):
        # Evitamos que Windows/Django duplique el hilo al recargar el servidor de desarrollo
        if os.environ.get('RUN_MAIN') == 'true':
            from monitor_app.scheduler import iniciar_orquestador
            iniciar_orquestador()