import subprocess
import platform
import threading
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Nodo, ConfiguracionGlobal

def barrido_red_local(request):
    # Detectar el sistema operativo para el comando de ping
    sistema = platform.system().lower()
    
    # Lista compartida para guardar las IPs que respondan
    ips_encontradas = []
    
    # Función que ejecutará cada hilo para una IP específica
    def escanear_ip(ip_destino):
        comando = ["ping", "-n", "2", "-w", "1500", ip_destino] if sistema == "windows" else ["ping", "-c", "2", "-W", "2s", ip_destino]
        try:
            resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            salida = resultado.stdout.lower()
            
            # Filtros estrictos para confirmar que el host REALMENTE respondió
            if resultado.returncode == 0 and salida:
                errores = ["inaccesible", "unreachable", "agotado", "timed out", "perdidos = 1", "loss = 100%"]
                if not any(err in salida for err in errores):
                    ips_encontradas.sappend(ip_destino)
        except Exception:
            pass

    # Creamos y lanzamos 254 hilos en paralelo (uno para cada IP del segmento)
    hilos = []
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        t = threading.Thread(target=escanear_ip, args=(ip,))
        hilos.append(t)
        t.start()

    # Esperamos a que todos los hilos terminen antes de continuar
    for t in hilos:
        t.join()

    # Registrar en la Base de Datos las IPs nuevas encontradas
    nuevos_nodos_contador = 0
    for ip_viva in ips_encontradas:
        # Si la IP ya está registrada, la ignoramos para no duplicar
        existe = Nodo.objects.filter(ip=ip_viva).exists()
        if not existe:
            Nodo.objects.create(
                nombre=f"AutoDescubierto-{ip_viva.split('.')[-1]}", # Ejemplo: AutoDescubierto-5
                ip=ip_viva,
                tecnologia="LAN", # Valor por defecto
                monitoreo_activo=True
            )
            nuevos_nodos_contador += 1

    # Enviar un mensaje de éxito a la interfaz de Django
    if nuevos_nodos_contador > 0:
        messages.success(request, f"¡Barrido completado! Se encontraron {len(ips_encontradas)} equipos vivos. Se agregaron {nuevos_nodos_contador} nuevos nodos al panel.")
    else:
        messages.info(request, f"Barrido completado. Se detectaron {len(ips_encontradas)} equipos, pero todos ya estaban registrados.")

    return redirect('dashboard') # Reemplaza por el nombre real de tu url de dashboard

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

from django.http import JsonResponse

def api_estatus_nodos(request):
    nodos = Nodo.objects.all()
    datos = []
    for nodo in nodos:
        # Obtenemos la última métrica de la misma forma que el dashboard
        if not nodo.monitoreo_activo:
            estado = "DESACTIVADO"
            latencia = "--"
        else:
            ultima = nodo.metricas.first()
            estado = ultima.estado if ultima else "SIN LECTURAS"
            latencia = f"{ultima.latencia} ms" if ultima else "--"
            
        datos.append({
            "id": nodo.id,
            "estado": estado,
            "latencia": latencia,
            "monitoreo_activo": nodo.monitoreo_activo
        })
    return JsonResponse({"nodos": datos})