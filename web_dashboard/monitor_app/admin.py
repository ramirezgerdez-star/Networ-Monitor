from django.contrib import admin

from .models import HistorialMetricas, Nodo, ConfiguracionGlobal

# Registramos los modelos para que sean visibles en el administrador
admin.site.register(Nodo)
admin.site.register(HistorialMetricas)
admin.site.register(ConfiguracionGlobal)