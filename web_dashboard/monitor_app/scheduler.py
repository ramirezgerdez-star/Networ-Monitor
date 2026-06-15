import threading
import time
import platform
import subprocess
import re
from monitor_app.models import Nodo, HistorialMetricas, ConfiguracionGlobal

def evaluar_nodo(ip, num_pings=1):
    import platform
    import subprocess
    import re

    sistema = platform.system().lower()
    comando = ["ping", "-n", str(num_pings), ip] if sistema == "windows" else ["ping", "-c", str(num_pings), ip]

    try:
        # Añadimos un timeout estricto para que no se quede colgado esperando IPs muertas
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
        salida = resultado.stdout

        if resultado.returncode == 0 and salida:
            # ---> CLAVE PARA WINDOWS: Si el texto contiene errores típicos de red, es OFFLINE
            errores_conexion = ["inaccesible", "unreachable", "agotado", "timed out", "perdidos = 1", "loss = 100%"]
            if any(error in salida.lower() for error in errores_conexion):
                return {"estado": "OFFLINE", "latencia": 0, "perdida": 100}

            # Si pasó el filtro de errores, buscamos la latencia real
            match_latencia = re.search(r"(?:Media|Average)\s*=\s*(\d+)ms", salida, re.IGNORECASE)
            if match_latencia:
                latencia = int(match_latencia.group(1))
                
                match_perdida = re.search(r"(\d+)%\s*(?:loss|de pérdida|perdidos|pérdida)", salida, re.IGNORECASE)
                perdida = int(match_perdida.group(1)) if match_perdida else 0
                
                estado = "ONLINE" if perdida < 20 else "DEGRADADO"
                return {"estado": estado, "latencia": latencia, "perdida": perdida}
            
            # Si no hay métrica de tiempo válida (Media = Xms), asumimos que no hay respuesta real
            return {"estado": "OFFLINE", "latencia": 0, "perdida": 100}
        else:
            return {"estado": "OFFLINE", "latencia": 0, "perdida": 100}
    except Exception:
        return {"estado": "OFFLINE", "latencia": 0, "perdida": 100}

def ciclo_monitoreo_segundo_plano():
    """Bucle infinito que corre en un hilo secundario de Django"""
    print("🚀 [DAEMON INTERNO] Iniciando hilos de escaneo nativos...")
    while True:
        # IMPORTANTE: Solo escaneamos nodos donde monitoreo_activo sea True
        for nodo in Nodo.objects.filter(monitoreo_activo=True):
    
            # 1. Llamas a tu función de ping actual
            resultado_ping = evaluar_nodo(nodo.ip, num_pings=1)
            
            # 2. Inicializas las velocidades de red por defecto
            mbps_down = 0.0
            mbps_up = 0.0
            
            # 3. Si el nodo está ONLINE y tiene el switch SNMP activo, llamamos a tu simulador
            if resultado_ping["estado"] == "ONLINE" and nodo.snmp_activo:
                mbps_down, mbps_up = simular_ancho_banda()  # Tu función que genera los Mbps
                
            # 4. Creamos el registro en la base de datos mapeando todos tus campos reales
            HistorialMetricas.objects.create(
                nodo=nodo,
                estado=resultado_ping["estado"],
                latencia=resultado_ping["latencia"],
                perdida=resultado_ping["perdida"],
                # Simulamos CPU y RAM si el switch SNMP está activo, sino van en None
                snmp_cpu=random.randint(15, 60) if nodo.snmp_activo else None,
                snmp_ram=random.randint(30, 75) if nodo.snmp_activo else None,
                # Guardamos las velocidades simuladas
                velocidad_max_download=mbps_down,
                velocidad_max_subida=mbps_up  # Recuerda haber agregado esta columna a tu modelo
            )

        # Consultamos el intervalo dinámico configurado por el usuario
        config, _ = ConfiguracionGlobal.objects.get_or_create(id=1)
        time.sleep(config.intervalo_snmp)

def iniciar_orquestador():
    """Lanza el hilo para que Django lo corra de fondo de forma asíncrona"""
    hilo = threading.Thread(target=ciclo_monitoreo_segundo_plano, daemon=True)
    hilo.start()

import random

def simular_ancho_banda():
    """Genera fluctuaciones realistas de carga y descarga en Mbps"""
    bajada = round(random.uniform(30.0, 85.0), 2)  # Fluctuaciones entre 30 y 85 Mbps
    subida = round(bajada * random.uniform(0.2, 0.4), 2) # Velocidad de subida asimétrica
    return bajada, subida