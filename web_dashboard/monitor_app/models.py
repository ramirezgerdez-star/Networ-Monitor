from django.db import models


class Nodo(models.Model):
    TECNOLOGIAS = [
        ("FO", "Fibra Óptica"),
        ("RE", "Radioenlace"),
        ("ETH", "Ethernet / Cobre"),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    ip = models.GenericIPAddressField(unique=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    tecnologia = models.CharField(
        max_length=3, choices=TECNOLOGIAS, default="FO"
    )

    # 1. CONTROL DE ESCANER: Para iniciar/detener el ping_worker desde el HTML
    monitoreo_activo = models.BooleanField(default=True)

    # 2. CONFIGURACIÓN SNMP (Para el futuro worker de SNMP)
    comunidad_snmp = models.CharField(
        max_length=50, default="public", blank=True
    )
    snmp_activo = models.BooleanField(default=False)

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        estado_scan = "ACTIVO" if self.monitoreo_activo else "INACTIVO"
        return f"{self.nombre} ({self.ip}) - [{estado_scan}]"


class HistorialMetricas(models.Model):
    ESTADOS = [
        ("ONLINE", "Online"),
        ("DEGRADADO", "Degradado"),
        ("OFFLINE", "Offline"),
    ]

    nodo = models.ForeignKey(
        Nodo, on_delete=models.CASCADE, related_name="metricas"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS)
    latencia = models.FloatField()
    perdida = models.IntegerField()

    # 3. MÉTRICAS EXTRA (Para SNMP y la prueba de velocidad máxima a un nodo específico)
    snmp_cpu = models.IntegerField(null=True, blank=True, help_text="Uso de CPU %")
    snmp_ram = models.IntegerField(null=True, blank=True, help_text="Uso de RAM %")
    velocidad_max_download = models.FloatField(
        null=True, blank=True, help_text="Mbps de Bajada (Speedtest)"
    )
    # En tu clase HistorialMetricas de models.py agrega:
    velocidad_max_subida = models.FloatField(null=True, blank=True, help_text="Mbps de Subida")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.nodo.nombre} - {self.estado} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
  
    
class ConfiguracionGlobal(models.Model):
    intervalo_snmp = models.IntegerField(default=10, help_text="Intervalo de escaneo en segundos")

    class Meta:
        verbose_name = "Configuración Global"
        verbose_name_plural = "Configuraciones Globales"

    def __str__(self):
        return f"Configuración Activa: {self.intervalo_snmp}s"