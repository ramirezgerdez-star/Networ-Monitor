import time
from pysnmp.hlapi import *

def consultar_oid_snmp(ip, comunidad, oid):
    """Consulta un OID específico vía SNMP v2c"""
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(comunidad, mpModel=1),
        UdpTransportTarget((ip, 161), timeout=2.0, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    if errorIndication or errorStatus:
        return None
    for varBind in varBinds:
        return int(varBind[1])
    return None

def medir_ancho_banda_snmp(ip, comunidad="public", interfaz_index="1"):
    """
    Calcula el ancho de banda real (Delta de Bytes / Delta de Tiempo)
    Devuelve: (bajada_mbps, subida_mbps)
    """
    # OIDs Estándar para bytes entrantes (bajada) y salientes (subida)
    OID_IN = f'1.3.6.1.2.1.2.2.1.10.{interfaz_index}'
    OID_OUT = f'1.3.6.1.2.1.2.2.1.16.{interfaz_index}'
    
    # Primera muestra
    bytes_in_1 = consultar_oid_snmp(ip, comunidad, OID_IN)
    bytes_out_1 = consultar_oid_snmp(ip, comunidad, OID_OUT)
    t1 = time.time()
    
    if bytes_in_1 is None or bytes_out_1 is None:
        return 0.0, 0.0
        
    # Esperar un breve intervalo para medir el diferencial (Delta)
    time.sleep(1.0)
    
    # Segunda muestra
    bytes_in_2 = consultar_oid_snmp(ip, comunidad, OID_IN)
    bytes_out_2 = consultar_oid_snmp(ip, comunidad, OID_OUT)
    t2 = time.time()
    
    delta_tiempo = t2 - t1
    
    # Calcular Bits por segundo y transformarlos a Megabits (Mbps)
    bps_bajada = ((bytes_in_2 - bytes_in_1) * 8) / delta_tiempo
    bps_subida = ((bytes_out_2 - bytes_out_1) * 8) / delta_tiempo
    
    mbps_bajada = round(bps_bajada / (1024 * 1024), 2)
    mbps_subida = round(bps_subida / (1024 * 1024), 2)
    
    return max(0.0, mbps_bajada), max(0.0, mbps_subida)