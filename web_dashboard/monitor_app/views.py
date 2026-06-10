from django.shortcuts import render, get_object_or_404, redirect
from .models import Nodo, ConfiguracionGlobal

def dashboard(request):
    nodos = Nodo.objects.all()
    
    # Obtenemos la configuración existente o creamos la primera por defecto
    config, _ = ConfiguracionGlobal.objects.get_or_create(id=1)
    
    for nodo in nodos:
        ultima_metrica = nodo.metricas.first()
        if ultima_metrica:
            nodo.ultimo_estado = ultima_metrica.estado
            nodo.ultima_latencia = f"{ultima_metrica.latencia} ms"
        else:
            nodo.ultimo_estado = "SIN DATOS"
            nodo.ultima_latencia = "--"
            
    return render(request, 'monitor_app/dashboard.html', {
        'nodos': nodos,
        'intervalo_actual': config.intervalo_snmp
    })

def actualizar_intervalo(request):
    if request.method == "POST":
        nuevo_intervalo = request.POST.get("intervalo")
        if nuevo_intervalo and nuevo_intervalo.isdigit():
            config, _ = ConfiguracionGlobal.objects.get_or_create(id=1)
            config.intervalo_snmp = int(nuevo_intervalo)
            config.save()
    return redirect('dashboard')

def toggle_nodo(request, nodo_id):
    nodo = get_object_or_404(Nodo, id=nodo_id)
    nodo.monitoreo_activo = not nodo.monitoreo_activo
    nodo.save()
    return redirect('dashboard')

from .models import HistorialMetricas

def vista_graficas(request):
    # 1. Cambiamos '-fecha' por '-timestamp' que es tu campo real de base de datos
    historial = HistorialMetricas.objects.all().order_by('-timestamp')[:30]
    historial = reversed(historial) # Mantenemos el orden de izquierda a derecha

    lista_tiempos = []
    lista_latencias = []
    lista_cpu = []
    lista_ram = []

    for registro in historial:
        # 2. Aquí también usamos registro.timestamp en lugar de registro.fecha
        if registro.timestamp:
            hora_formateada = registro.timestamp.strftime('%H:%M:%S')
        else:
            hora_formateada = "--:--:--"
            
        etiqueta = f"{hora_formateada} ({registro.nodo.nombre})"
        
        lista_tiempos.append(etiqueta)
        lista_latencias.append(float(registro.latencia))
        lista_cpu.append(registro.snmp_cpu if registro.snmp_cpu else 0)
        lista_ram.append(registro.snmp_ram if registro.snmp_ram else 0)

    return render(request, 'monitor_app/graficas.html', {
        'lista_tiempos': lista_tiempos,
        'lista_latencias': lista_latencias,
        'lista_cpu': lista_cpu,
        'lista_ram': lista_ram
    })