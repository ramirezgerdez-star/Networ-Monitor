"""
URL configuration for web_dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from monitor_app.views import dashboard, toggle_nodo, actualizar_intervalo, vista_graficas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'), # Nuestra página principal limpia
    path('toggle/<int:nodo_id>/', toggle_nodo, name='toggle_nodo'), # URL interna para el botón de control
    path('graficas/', vista_graficas, name='vista_graficas'), # URL para la vista de gráficas   
    path('actualizar-intervalo/', actualizar_intervalo, name='actualizar_intervalo'), # NUEVA URL para actualizar el intervalo desde el formulario
]
