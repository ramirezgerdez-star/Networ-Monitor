import os
import sys
import time
import platform
import subprocess
import re
import django

# --- CONFIGURACIÓN DE ENTORNO DJANGO ---
ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_dashboard'))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_dashboard.settings")
django.setup()

from monitor_app.models import Nodo, HistorialMetricas

# --- MOTOR DE RED OPTIMIZADO Y BILINGÜE ---
def evaluar_nodo(ip, num_pings=4):
    sistema = platform.system().lower()
    comando = ["ping", "-n", str(num_pings), ip] if sistema == "windows" else ["ping", "-c", str(num_pings), ip]

    try:
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
        salida = resultado.stdout

        # Si el comando ping de Windows termina con código 0 y hay texto, el equipo está vivo
        if resultado.returncode == 0 and salida:
            # Buscamos el tiempo promedio (Media = Xms o Average = Xms)
            match_latencia = re.search(r"(?:Media|Average)\s*=\s*(\d+)ms", salida, re.IGNORECASE)
            latencia = int(match_latencia.group(1)) if match_latencia else 15.0
            
            # Buscamos la pérdida de paquetes
            match_perdida = re.search(r"(\d+)%\s*(?:loss|de pérdida|perdidos|pérdida)", salida, re.IGNORECASE)
            perdida = int(match_perdida.group(1)) if match_perdida else 0
            
            estado = "ONLINE" if perdida < 20 else "DEGRADADO"
            return {"estado": estado, "latencia": latencia, "perdida": perdida}
        
        else:
            # Si el código de retorno es diferente de 0, el equipo no respondió
            return {"estado": "OFFLINE", "latencia": 0, "perdida": 100}

    except Exception as e:
        return {"estado": "ERROR", "latencia": 0, "perdida": 100, "detalle": str(e)}

# --- FUNCIÓN DE MONITOREO CÍCLICO ---
def ejecutar_monitoreo():
    print("\n=== Iniciando Ciclo de Monitoreo en la Base de Datos ===")
    
    nodos = Nodo.objects.all()
    
    if not nodos:
        print("No hay nodos registrados en la base de datos.")
        return

    print(f"Se encontraron {nodos.count()} nodos para evaluar.")

    for nodo in nodos:
        print(f"Evaluando: {nodo.nombre} [{nodo.ip}]...")
        reporte = evaluar_nodo(nodo.ip)
        
        # Inserción directa en el Historial cronológico para Chart.js
        metrica = HistorialMetricas.objects.create(
            nodo=nodo,
            estado=reporte['estado'],
            latencia=reporte['latencia'],
            perdida=reporte['perdida']
        )
        
        print(f"  -> Resultado: {metrica.estado} | {metrica.latencia}ms | {metrica.perdida}% pérdida")
        print(f"  -> ¡Métrica guardada en BD con éxito ID: {metrica.id}!")

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" DAEMON PING CORRIENDO Y SINCRONIZADO CON EL PANEL ")
    print("="*60)
    
    from monitor_app.models import ConfiguracionGlobal

    try:
        while True:
            ejecutar_monitoreo() 
            
            config, _ = ConfiguracionGlobal.objects.get_or_create(id=1)
            INTERVALO_DINAMICO = config.intervalo_snmp
            
            print(f"\n[💤] Sincronizado: Esperando {INTERVALO_DINAMICO} segundos para el siguiente ciclo de Ping... (Ctrl+C para salir)")
            time.sleep(INTERVALO_DINAMICO)
            
    except KeyboardInterrupt:
        print("\n[-] Escáner de Ping detenido por el usuario. ¡Hasta luego!")