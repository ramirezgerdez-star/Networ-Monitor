# 🌐 NetMonitor Pro

NetMonitor Pro es una solución de telemetría y monitoreo de redes en tiempo real. Está diseñado para ofrecer una visibilidad profunda del estado de salud de dispositivos de red (Routers, Switches, Servidores) mediante la implementación de agentes de recolección asíncronos y una interfaz de visualización dinámica.

## 🚀 Arquitectura del Sistema
El sistema se divide en tres capas fundamentales que trabajan de forma sincronizada:

1. CAPA DE RECOLECCIÓN (Workers): Scripts independientes en Python que realizan consultas SNMP y PING continuas. La naturaleza asíncrona asegura que la interfaz web nunca se bloquee, sin importar cuántos nodos estés monitoreando.

2. CAPA DE GESTIÓN (Backend Django): Actúa como el cerebro del sistema. Gestiona la persistencia de datos, los modelos de nodos y expone los puntos finales (API endpoints) con telemetría limpia.

3. CAPA DE VISUALIZACIÓN (Frontend): Interfaz construida con Bootstrap y Chart.js. Utiliza el patrón de "Osciloscopio" para renderizar cambios en tiempo real, permitiendo una rápida identificación de picos de tráfico o fallas de latencia.

## 🛠️ Requisitos del Sistema
- Python 3.x
- Django 4.x
- Protocolo SNMP habilitado en los dispositivos remotos (Comunidad v2c).
- Permisos de ejecución para procesos en segundo plano.

## ⚙️ Configuración y Despliegue
Para poner en marcha el entorno de desarrollo:

1. Clonar el repositorio: git clone [URL_DE_TU_REPOSITORIO]
2. Entorno virtual: python -m venv venv
3. Dependencias: pip install -r requirements.txt
4. Migraciones: python manage.py migrate
5. Ejecución de Workers (abrir 2 terminales):
   - python manage.py run_ping_worker
   - python manage.py run_snmp_worker
6. Servidor Web: python manage.py runserver

## 💡 Notas sobre el Osciloscopio
El sistema utiliza una arquitectura de polling de alta frecuencia. Si notas que la línea de datos se queda plana en 0, asegúrate de que:
- La variable ancho_banda_bajada y ancho_banda_subida estén siendo inyectadas correctamente desde el JSON de la API.
- El navegador esté procesando los datos como float y no como string.

## 📈 Roadmap (Futuras Mejoras)
- Implementación de alertas por correo electrónico/Telegram cuando un nodo caiga.
- Histórico de largo plazo mediante persistencia de base de datos optimizada.
- Autenticación de usuarios para acceso restringido al dashboard.

## 📄 Licencia
Este proyecto es de código abierto bajo la Licencia MIT.
